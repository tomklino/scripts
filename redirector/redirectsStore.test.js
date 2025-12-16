const { test, beforeEach, afterEach } = require('node:test')
const assert = require('node:assert/strict')
const fs = require('node:fs')
const path = require('node:path')
const RedirectsStore = require('./redirectsStore')

function tmpFile(name) {
  return path.join(__dirname, `.tmp_${Date.now()}_${Math.random().toString(36).slice(2)}_${name}.json`)
}

let dataFile
let store

beforeEach(() => {
  dataFile = tmpFile('store')
  store = new RedirectsStore(dataFile)
})

afterEach(() => {
  if (fs.existsSync(dataFile)) fs.unlinkSync(dataFile)
})

test('set/get exact mapping persists to file', () => {
  store.setExactMapping('/a', 'https://x')
  assert.equal(store.getExactMapping('/a'), 'https://x')
  const json = JSON.parse(fs.readFileSync(dataFile, 'utf8'))
  assert.equal(json.exact['/a'], 'https://x')
})

test('set/get prefix mapping persists to file', () => {
  store.setPrefixMapping('/b', 'https://y')
  assert.equal(store.getPrefixMapping('/b'), 'https://y')
  const json = JSON.parse(fs.readFileSync(dataFile, 'utf8'))
  assert.equal(json.prefix['/b'], 'https://y')
})

test('loads mappings from file on construction', () => {
  const pre = { exact: { '/a': 'https://x' }, prefix: { '/b': 'https://y' } }
  fs.writeFileSync(dataFile, JSON.stringify(pre), 'utf8')

  const s2 = new RedirectsStore(dataFile)
  assert.equal(s2.getExactMapping('/a'), 'https://x')
  assert.equal(s2.getPrefixMapping('/b'), 'https://y')
})

test('set/get proxy mapping persists to file', () => {
  store.setProxyMapping('api.example.com', 'https://backend.example.com')
  assert.equal(store.getProxyMapping('api.example.com'), 'https://backend.example.com')
  const json = JSON.parse(fs.readFileSync(dataFile, 'utf8'))
  assert.equal(json.proxy['api.example.com'], 'https://backend.example.com')
})

test('loads proxy mappings from file on construction', () => {
  const pre = {
    exact: {},
    prefix: {},
    proxy: { 'api.example.com': 'https://backend.example.com' }
  }
  fs.writeFileSync(dataFile, JSON.stringify(pre), 'utf8')

  const s2 = new RedirectsStore(dataFile)
  assert.equal(s2.getProxyMapping('api.example.com'), 'https://backend.example.com')
})


