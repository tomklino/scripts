const { test, before, after } = require('node:test');
const assert = require('node:assert/strict');
const http = require('node:http');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');

function request(method, url, { headers = {} } = {}) {
  return new Promise((resolve, reject) => {
    const u = new URL(url);
    const options = {
      method,
      hostname: u.hostname,
      port: u.port,
      path: u.pathname + u.search,
      headers
    };
    const req = http.request(options, (res) => {
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: Buffer.concat(chunks).toString('utf8')
        });
      });
    });
    req.on('error', reject);
    req.end();
  });
}

function spawnServer({ port, dataFile }) {
  const env = { ...process.env, PORT: String(port), REDIRECTS_FILE: dataFile };
  const child = spawn(process.execPath, [path.join(__dirname, 'redirector.js')], {
    env,
    stdio: ['ignore', 'pipe', 'pipe']
  });
  return child;
}

async function waitForServer(port, timeoutMs = 3000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await request('GET', `http://127.0.0.1:${port}/__health`);
      // 404 means server is up
      if (res.statusCode >= 200) return;
    } catch (_) {}
    await new Promise((r) => setTimeout(r, 50));
  }
  throw new Error('Server did not start in time');
}

function randomPort() {
  return 3000 + Math.floor(Math.random() * 1000);
}

function tmpFile(name) {
  return path.join(__dirname, `.tmp_${Date.now()}_${Math.random().toString(36).slice(2)}_${name}.json`);
}

let child;
let port;
let dataFile;
let mockBackend;
let mockPort;

before(async () => {
  port = randomPort();
  mockPort = randomPort();
  dataFile = tmpFile('redirects');

  mockBackend = http.createServer((req, res) => {
    const chunks = [];
    req.on('data', (c) => chunks.push(c));
    req.on('end', () => {
      const body = Buffer.concat(chunks).toString('utf8');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        method: req.method,
        path: req.url,
        host: req.headers.host,
        headers: req.headers,
        body: body || undefined
      }));
    });
  });
  mockBackend.listen(mockPort);

  child = spawnServer({ port, dataFile });
  await waitForServer(port);
});

after(() => {
  if (child) child.kill();
  if (mockBackend) mockBackend.close();
  if (dataFile && fs.existsSync(dataFile)) fs.unlinkSync(dataFile);
});

test('1. PUT "to" creates mapping', async () => {
  const res = await request('PUT', `http://127.0.0.1:${port}/g?to=https://google.com`);
  assert.equal(res.statusCode, 201);
  const body = JSON.parse(res.body);
  assert.equal(body.source, '/g');
  assert.equal(body.to, 'https://google.com');
});

test('2. GET "to" follows redirect', async () => {
  const res = await request('GET', `http://127.0.0.1:${port}/g`);
  assert.equal(res.statusCode, 302);
  assert.equal(res.headers.location, 'https://google.com');
});

test('3. PUT "topattern" creates prefix mapping', async () => {
  const res = await request('PUT', `http://127.0.0.1:${port}/path?topattern=https://example.com/base`);
  assert.equal(res.statusCode, 201);
  const body = JSON.parse(res.body);
  assert.equal(body.sourceBase, '/path');
  assert.equal(body.toBase, 'https://example.com/base');
});

test('4. GET "topattern" via path redirects with suffix', async () => {
  const res = await request('GET', `http://127.0.0.1:${port}/path/abc/def`);
  assert.equal(res.statusCode, 302);
  assert.equal(res.headers.location, 'https://example.com/base/abc/def');
});

test('5. GET "topattern" via host redirects', async () => {
  // Create host-based prefix mapping by base '/example.com'
  const put = await request('PUT', `http://127.0.0.1:${port}/example.com?topattern=https://hostdest.com`);
  assert.equal(put.statusCode, 201);
  const res = await request('GET', `http://127.0.0.1:${port}/foo/bar`, {
    headers: { Host: 'example.com' }
  });
  assert.equal(res.statusCode, 302);
  assert.equal(res.headers.location, 'https://hostdest.com/foo/bar');
});

test('6. persistence: save and load from file', async () => {
  // Ensure exact and prefix exist in file
  const res1 = await request('PUT', `http://127.0.0.1:${port}/persist?to=https://persisted.com`);
  assert.equal(res1.statusCode, 201);
  const res2 = await request('PUT', `http://127.0.0.1:${port}/keep?topattern=https://ke.pt`);
  assert.equal(res2.statusCode, 201);

  // Kill server and restart with same data file and new port to avoid conflicts
  if (child) child.kill();
  port = randomPort();
  child = spawnServer({ port, dataFile });
  await waitForServer(port);

  // Exact still works
  const g = await request('GET', `http://127.0.0.1:${port}/persist`);
  assert.equal(g.statusCode, 302);
  assert.equal(g.headers.location, 'https://persisted.com');

  // Prefix still works
  const p = await request('GET', `http://127.0.0.1:${port}/keep/ok`);
  assert.equal(p.statusCode, 302);
  assert.equal(p.headers.location, 'https://ke.pt/ok');
});

test('7. PUT proxy creates host-based proxy mapping', async () => {
  const res = await request('PUT', `http://127.0.0.1:${port}/?host=api.test.com&proxy=http://127.0.0.1:${mockPort}`);
  assert.equal(res.statusCode, 201);
  const body = JSON.parse(res.body);
  assert.equal(body.host, 'api.test.com');
  assert.equal(body.proxy, `http://127.0.0.1:${mockPort}`);
});

test('8. GET with proxy host forwards request to backend', async () => {
  await request('PUT', `http://127.0.0.1:${port}/?host=proxy.test.com&proxy=http://127.0.0.1:${mockPort}`);
  const res = await request('GET', `http://127.0.0.1:${port}/api/users/123`, {
    headers: { Host: 'proxy.test.com' }
  });
  assert.equal(res.statusCode, 200);
  const body = JSON.parse(res.body);
  assert.equal(body.method, 'GET');
  assert.equal(body.path, '/api/users/123');
  assert.equal(body.host, `127.0.0.1:${mockPort}`);
});

test('9. PUT with proxy host forwards to backend instead of configuring', async () => {
  await request('PUT', `http://127.0.0.1:${port}/?host=proxy.put.com&proxy=http://127.0.0.1:${mockPort}`);
  const res = await request('PUT', `http://127.0.0.1:${port}/api/update?to=ignored`, {
    headers: { Host: 'proxy.put.com' }
  });
  assert.equal(res.statusCode, 200);
  const body = JSON.parse(res.body);
  assert.equal(body.method, 'PUT');
  assert.equal(body.path, '/api/update?to=ignored');
  assert.equal(body.host, `127.0.0.1:${mockPort}`);
});


