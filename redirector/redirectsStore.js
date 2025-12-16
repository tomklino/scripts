const fs = require('fs')

class RedirectsStore {
  constructor(dataFilePath) {
    this.dataFilePath = dataFilePath
    this.redirects = new Map()
    this.prefixRedirects = new Map()
    this.proxies = new Map()
    this._loadRedirects()
  }

  _persistRedirects() {
    const payload = {
      exact: Object.fromEntries(this.redirects.entries()),
      prefix: Object.fromEntries(this.prefixRedirects.entries()),
      proxy: Object.fromEntries(this.proxies.entries())
    };
    try {
      fs.writeFileSync(this.dataFilePath, JSON.stringify(payload, null, 2), 'utf8');
    } catch (err) {
      const e = new Error('Failed to persist redirects')
      e.cause = err
      throw e
    }
  }

  _loadRedirects() {
    try {
      if (!fs.existsSync(this.dataFilePath)) return;
      const raw = fs.readFileSync(this.dataFilePath, 'utf8');
      if (!raw) return;
      const parsed = JSON.parse(raw);
      if (parsed && parsed.exact && typeof parsed.exact === 'object') {
        for (const [k, v] of Object.entries(parsed.exact)) {
          this.redirects.set(k, v);
        }
      }
      if (parsed && parsed.prefix && typeof parsed.prefix === 'object') {
        for (const [k, v] of Object.entries(parsed.prefix)) {
          this.prefixRedirects.set(k, v);
        }
      }
      if (parsed && parsed.proxy && typeof parsed.proxy === 'object') {
        for (const [k, v] of Object.entries(parsed.proxy)) {
          this.proxies.set(k, v);
        }
      }
    } catch (err) {
      const e = new Error('Failed to load redirects')
      e.cause = err
      throw e
    }
  }

  setExactMapping(sourcePath, destinationUrl) {
    this.redirects.set(sourcePath, destinationUrl);
    this._persistRedirects();
  }
  
  setPrefixMapping(basePath, destinationBaseUrl) {
    this.prefixRedirects.set(basePath, destinationBaseUrl);
    this._persistRedirects();
  }
  
  getExactMapping(sourcePath) {
    return this.redirects.get(sourcePath)
  }

  getPrefixMapping(sourcePath) {
    return this.prefixRedirects.get(sourcePath)
  }

  setProxyMapping(hostname, destinationUrl) {
    this.proxies.set(hostname, destinationUrl);
    this._persistRedirects();
  }

  getProxyMapping(hostname) {
    return this.proxies.get(hostname)
  }
}

module.exports = RedirectsStore