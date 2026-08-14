'use strict';

/**
 * MD2HTMLClient — Node.js SDK for the MD2HTML API.
 *
 * The MD2HTML API converts Markdown to HTML (and offers a few small text
 * utilities) behind a micropayment billing layer. This client wraps all 10
 * public endpoints with a thin fetch-based interface.
 *
 * Requirements: Node.js 18+ (global fetch). No external dependencies.
 *
 * Quick start:
 *   const { MD2HTMLClient } = require('./md2html-client');
 *   const client = new MD2HTMLClient({ apiKey: 'mk_...' });
 *   const { html } = await client.convert('# Hello **world**');
 *
 * All methods are async and return the parsed JSON response body. On a non-2xx
 * status they reject with an Error that carries `.status`, `.url`, and the
 * parsed response body (when available) under `.body`.
 */

const DEFAULT_BASE_URL = 'http://147.15.103.217/md2html';
const DEFAULT_TIMEOUT_MS = 30000;

class MD2HTMLClient {
  /**
   * @param {Object}  [opts]
   * @param {string}  [opts.baseUrl]   Base URL including the /md2html mount path.
   * @param {string}  [opts.apiKey]    API key (mk_...). Sent as X-API-Key. Optional.
   * @param {number}  [opts.timeoutMs] Request timeout in milliseconds.
   * @param {Object}  [opts.headers]   Extra default headers merged into every request.
   * @param {typeof fetch} [opts.fetch] Custom fetch implementation (testing).
   */
  constructor(opts = {}) {
    if (opts !== null && typeof opts !== 'object') {
      throw new TypeError('MD2HTMLClient: opts must be an object');
    }
    this.baseUrl = (opts.baseUrl || DEFAULT_BASE_URL).replace(/\/+$/, '');
    this.apiKey = opts.apiKey || null;
    this.timeoutMs = opts.timeoutMs || DEFAULT_TIMEOUT_MS;
    this.extraHeaders = opts.headers || {};
    this._fetch = opts.fetch || (typeof fetch !== 'undefined' ? fetch : null);
    if (!this._fetch) {
      throw new Error(
        'MD2HTMLClient: global fetch is unavailable. Use Node.js 18+ or pass opts.fetch.'
      );
    }
  }

  // ---- internals -----------------------------------------------------------

  /** Build an absolute URL from a path relative to baseUrl. */
  _url(path) {
    return `${this.baseUrl}${path}`;
  }

  /** Default headers for every request. */
  _defaultHeaders() {
    const h = Object.assign({}, this.extraHeaders);
    if (this.apiKey) h['X-API-Key'] = this.apiKey;
    return h;
  }

  /**
   * Core request helper. Always sends Accept: application/json and (for POST)
   * Content-Type: application/json unless overridden by callOptions.headers.
   * @private
   */
  async _request(method, path, { body, headers, signal } = {}) {
    const url = this._url(path);
    const reqHeaders = Object.assign(
      { Accept: 'application/json' },
      this._defaultHeaders(),
      headers || {}
    );

    const init = {
      method,
      headers: reqHeaders,
      signal,
    };

    if (body !== undefined) {
      if (typeof body === 'string') {
        init.body = body;
        if (!('Content-Type' in reqHeaders)) reqHeaders['Content-Type'] = 'text/plain';
      } else {
        init.body = JSON.stringify(body);
        if (!('Content-Type' in reqHeaders)) reqHeaders['Content-Type'] = 'application/json';
      }
    }

    // Enforce a timeout via AbortController (does not override caller's signal).
    let timeoutController;
    let timedOut = false;
    if (!signal) {
      timeoutController = new AbortController();
      init.signal = timeoutController.signal;
      setTimeout(() => {
        timedOut = true;
        timeoutController.abort();
      }, this.timeoutMs);
    }

    let res;
    try {
      res = await this._fetch(url, init);
    } catch (err) {
      if (timedOut || (err && err.name === 'AbortError')) {
        throw new Error(`MD2HTMLClient: request to ${url} timed out after ${this.timeoutMs}ms`);
      }
      throw new Error(`MD2HTMLClient: network error requesting ${url}: ${err.message}`);
    }

    const text = await res.text();
    let parsed;
    try {
      parsed = text ? JSON.parse(text) : null;
    } catch (_) {
      parsed = text;
    }

    if (!res.ok) {
      const e = new Error(
        `MD2HTMLClient: ${method} ${path} failed with status ${res.status}`
      );
      e.status = res.status;
      e.url = url;
      e.body = parsed;
      throw e;
    }
    return parsed;
  }

  // ---- public endpoints ----------------------------------------------------

  /**
   * POST /convert — Convert a Markdown string to HTML.
   * @param {string} markdown                Markdown source.
   * @param {Object} [opts]
   * @param {string} [opts.apiKey]            One-off API key override for this call.
   * @returns {Promise<{html:string, billing?:Object, warning?:string}>}
   */
  async convert(markdown, opts = {}) {
    if (typeof markdown !== 'string') {
      throw new TypeError('convert(markdown): expected a string');
    }
    const headers = {};
    if (opts.apiKey) headers['X-API-Key'] = opts.apiKey;
    return this._request('POST', '/convert', { body: { markdown }, headers });
  }

  /**
   * POST /json/prettify — Re-indent a compact JSON string with 2-space pretty printing.
   * @param {string} json  A compact JSON string, e.g. '{"a":1,"b":2}'.
   * @returns {Promise<Object>} Prettified JSON string plus a billing object.
   */
  async jsonPrettify(json) {
    if (typeof json !== 'string') {
      throw new TypeError('jsonPrettify(json): expected a JSON string');
    }
    return this._request('POST', '/json/prettify', { body: { json } });
  }

  /**
   * POST /text/stats — Word/char counts, reading time, and top words for a text.
   * @param {string} text
   * @returns {Promise<{words:number, chars:number, chars_no_spaces:number,
   *                     reading_time_min:number, top_words:Array, billing?:Object}>}
   */
  async textStats(text) {
    if (typeof text !== 'string') {
      throw new TypeError('textStats(text): expected a string');
    }
    return this._request('POST', '/text/stats', { body: { text } });
  }

  /**
   * POST /slug — Generate a URL-safe slug from a title.
   * @param {string} title
   * @returns {Promise<{slug:string, billing?:Object}>}
   */
  async slug(title) {
    if (typeof title !== 'string') {
      throw new TypeError('slug(title): expected a string');
    }
    return this._request('POST', '/slug', { body: { title } });
  }

  /**
   * GET /register — Mint a new API key and its associated wallet address.
   * @returns {Promise<{api_key:string, wallet_address:string,
   *                     free_tier_limit:number, calls_made:number, remaining:number}>}
   */
  async register() {
    return this._request('GET', '/register');
  }

  /**
   * GET /health — Liveness probe. Returns service uptime and status JSON. No auth.
   * @returns {Promise<{status:string, version?:string, uptime_seconds:number, port:number}>}
   */
  async health() {
    return this._request('GET', '/health');
  }

  /**
   * GET /docs — Interactive API documentation (auto-generated).
   * @returns {Promise<string|Object>} The docs page body (text or JSON depending on server).
   */
  async docs() {
    return this._request('GET', '/docs', { headers: { Accept: 'text/plain, application/json' } });
  }

  /**
   * GET /payment — Returns the LTC wallet address for topping up quota.
   * @returns {Promise<{wallet_address:string, currency:string}>}
   */
  async payment() {
    return this._request('GET', '/payment');
  }

  /** POST /payment/claim — Verify a confirmed LTC txid and add prepaid calls. */
  async claimPayment(txid, opts = {}) {
    if (typeof txid !== 'string' || !/^[0-9a-fA-F]{64}$/.test(txid.trim())) {
      throw new TypeError('claimPayment(txid): expected 64 hexadecimal characters');
    }
    const apiKey = opts.apiKey || this.apiKey;
    if (!apiKey) {
      throw new Error('claimPayment(txid): an API key is required');
    }
    return this._request('POST', '/payment/claim', {
      body: { txid: txid.trim() },
      headers: { 'X-API-Key': apiKey },
    });
  }

  /**
   * GET /usage — Current quota usage for the caller (API key or IP).
   * @param {Object} [opts]
   * @param {string} [opts.apiKey] One-off API key override.
   * @returns {Promise<{calls_made:number, remaining:number}>}
   */
  async usage(opts = {}) {
    const headers = {};
    if (opts.apiKey) headers['X-API-Key'] = opts.apiKey;
    return this._request('GET', '/usage', { headers });
  }

  /**
   * GET /stats — Aggregate, public, read-only service metrics.
   * @returns {Promise<{total_calls:number, unique_ips:number}>}
   */
  async stats() {
    return this._request('GET', '/stats');
  }
}

// ---- CommonJS + ESM dual export ------------------------------------------

module.exports = { MD2HTMLClient };
module.exports.MD2HTMLClient = MD2HTMLClient;
module.exports.default = MD2HTMLClient;

// `Object.defineProperty` makes default-ESM-import interop work without
// breaking `require('./md2html-client').MD2HTMLClient`.
if (typeof Symbol !== 'undefined' && Symbol.toStringTag) {
  MD2HTMLClient.prototype[Symbol.toStringTag] = 'MD2HTMLClient';
}
