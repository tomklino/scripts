const http = require('http');
const { URL } = require('url');
const path = require('path');
const RedirectsStore = require('./redirectsStore')
const {
  redirect,
  notFound,
  methodNotAllowed,
  sendJson,
  proxyRequest
} = require('./httpReplies')
const { isValidDestination } = require('./validators');

// init redirects store
const DATA_FILE = process.env.REDIRECTS_FILE || path.join(__dirname, 'redirects.json');
const redirectsStore = new RedirectsStore(DATA_FILE)

function isHostRedirection(hostHeader) {
  return hostHeader &&
    ['localhost', '127.0.0.1', process.env.HOSTNAME]
    .every(h => h !== hostHeader)
}

const server = http.createServer((req, res) => {
  const requestUrl = new URL(req.url, 'http://localhost');
  const pathname = requestUrl.pathname;

  const hostHeader = (req.headers.host || '').split(':')[0];
  const proxyDest = redirectsStore.getProxyMapping(hostHeader);
  if (proxyDest) {
    return proxyRequest(req, res, proxyDest);
  }

  if (req.method === 'PUT') {
    const destination = requestUrl.searchParams.get('to');
    const destinationPattern = requestUrl.searchParams.get('topattern');
    const proxyHost = requestUrl.searchParams.get('host');
    const proxyDestination = requestUrl.searchParams.get('proxy');

    if (!destination && !destinationPattern && (!proxyHost || !proxyDestination)) {
      return sendJson(res, 400, { error: 'Missing "to", "topattern", or "host" and "proxy" query parameters' });
    }

    const providedParams = [destination, destinationPattern, (proxyHost && proxyDestination)].filter(Boolean);
    if (providedParams.length > 1) {
      return sendJson(res, 400, { error: 'Provide only one of "to", "topattern", or "host" and "proxy"' });
    }

    if (proxyHost && proxyDestination) {
      if (!isValidDestination(proxyDestination)) {
        return sendJson(res, 400, { error: 'Invalid proxy URL; must be http(s)://' });
      }
      redirectsStore.setProxyMapping(proxyHost, proxyDestination);
      return sendJson(res, 201, { host: proxyHost, proxy: proxyDestination });
    }

    if (destination) {
      if (!isValidDestination(destination)) {
        return sendJson(res, 400, { error: 'Invalid destination URL; must be http(s)://' });
      }
      redirectsStore.setExactMapping(pathname, destination);
      return sendJson(res, 201, { source: pathname, to: destination });
    }

    if (!isValidDestination(destinationPattern)) {
      return sendJson(res, 400, { error: 'Invalid topattern URL; must be http(s)://' });
    }

    const nextSlash = pathname.indexOf('/', 1);
    if (nextSlash !== -1) {
      return sendJson(res, 400, { error: 'topattern requires single-segment base path like "/path"' });
    }
    redirectsStore.setPrefixMapping(pathname, destinationPattern);
    return sendJson(res, 201, { sourceBase: pathname, toBase: destinationPattern });
  }

  if (req.method === 'GET') {
    const destination = redirectsStore.getExactMapping(pathname);
    if (destination) {
      return redirect(res, destination);
    }

    const pathParts = pathname.split('/').slice(1)
    // Hostname-based prefix redirect: if host header is not the HOST, treat '/<host>' as base    
    const sourcePath = isHostRedirection(hostHeader) ? `/${hostHeader}` : `/${pathParts.shift()}`

    const destBase = redirectsStore.getPrefixMapping(sourcePath)
    if(destBase) {
      const normalizedDestBase = destBase.replace(/\/+$/, '');
      const suffix = pathParts.join('/')
      const location = `${normalizedDestBase}/${suffix}`;
      return redirect(res, location)
    }

    const destPath = redirectsStore.getPrefixMapping(sourcePath)
    if (destPath) {

    }

    return notFound(res, pathname);
  }

  return methodNotAllowed(res);
});

const port = process.env.PORT ? Number(process.env.PORT) : 3000;
server.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`Redirector listening on http://localhost:${port}`);
});
