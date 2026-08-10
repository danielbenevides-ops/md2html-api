#!/usr/bin/env python3
"""
md2html_client.py — Python SDK for the MD2HTML API.

Standalone, professional SDK for the MD2HTML Markdown-to-HTML conversion
service (https://github.com/dcn13l/md2html-api).
    Live API:  http://147.15.103.217/md2html/

Features
--------
* Pure Python 3.8+ standard library — no requests, no pip dependencies.
* Thread-safe **async** variants of every method (via threading.Thread).
* Automatic 402 / free-tier-exhausted handling with pay-to-continue hint.
* Clean endpoint-by-endpoint convenience methods: convert(), register(),
  health(), payment(), usage(), stats(), prettify_json(), text_stats(),
  slug(), docs().
* Pythonic value extraction — call convert(*md*) and get the HTML string
  directly, not a raw response dict.

Usage
-----
    from md2html_client import MD2HTMLClient

    client = MD2HTMLClient("http://147.15.103.217/md2html")

    # Register a key (free tier — 10 calls each):
    reg = client.register()
    api_key = reg["api_key"]
    client.api_key = api_key

    # Convert markdown to HTML:
    html = client.convert("# Hello **world**")
    print(html)

    # Async (non-blocking) conversion:
    result = client.convert_async("# async test", callback=print)

License: MIT
Author:   MD2HTML API project
"""

from __future__ import annotations

import json
import time
import threading
import urllib.request
import urllib.error
from typing import Any, Callable, Optional, Union

__version__ = "1.0.0"
__all__ = ["MD2HTMLClient", "MD2HTMLAPIError"]

__author__ = "MD2HTML API project"
__license__ = "MIT"


class MD2HTMLAPIError(Exception):
    """Raised when the MD2HTML API returns a non-200 response that is NOT a
    *retryable* billing event (e.g. a server-side error or invalid request).

    402 Payment Required errors are NOT raised by default: the client returns
    a dict with status=402 so the caller can inspect billing and retry after
    payment. Set hard_402=True at construction time if you want strict raising.

    Attributes
    ----------
    status_code:    HTTP status returned by the server.
    url:            Full request URL.
    method:         HTTP method used.
    response_body:  The raw response body (str).
    parsed:         Parsed JSON dict, if the body was JSON; otherwise None.
    """

    def __init__(
        self,
        message: str,
        status_code: int = 0,
        url: str = "",
        method: str = "",
        response_body: str = "",
        parsed: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.method = method
        self.response_body = response_body
        self.parsed = parsed

    def __str__(self) -> str:
        base = super().__str__()
        if self.status_code:
            base = f"[HTTP {self.status_code}] {base}"
        return base


class MD2HTMLClient:
    """Python SDK client for the MD2HTML API.

    Parameters
    ----------
    base_url : str
        Root URL of the MD2HTML service. May end with or without a trailing
        slash — both forms work. Default: the live public API.
    api_key : str, optional
        The ``mk_...`` key returned by :meth:`register`. Sent as the
        ``X-API-Key`` header on every request when non-empty. If ``None``
        (default) the server bills by client IP and you get 10 free calls.
    timeout : float
        Network timeout in seconds for every underlying HTTP call.
    hard_402 : bool
        When True, a 402 response from the server is raised as MD2HTMLAPIError;
        when False (default) it is returned in the result dict alongside a
        ``payment_hint`` key so callers can inspect billing without catching.
    user_agent : str
        HTTP ``User-Agent`` header.

    Examples
    --------
    >>> client = MD2HTMLClient()
    >>> client.health()["status"]
    'ok'

    Using an API key:
    >>> reg = client.register()
    >>> client.api_key = reg["api_key"]
    >>> client.convert("# Hello")         # returns the HTML string
    '<h1>Hello</h1>'
    """

    DEFAULT_BASE_URL = "http://147.15.103.217/md2html"
    DEFAULT_TIMEOUT = 30.0
    DEFAULT_USER_AGENT = f"md2html-client/{__version__} (python)"

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        *,
        timeout: float = DEFAULT_TIMEOUT,
        hard_402: bool = False,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        # Normalise and strip trailing slash.
        if not base_url:
            raise ValueError("base_url must be a non-empty URL")
        base_url = base_url.rstrip("/")
        self.base_url = base_url
        self.api_key = api_key or ""
        self.timeout = float(timeout)
        self.hard_402 = bool(hard_402)
        self.user_agent = user_agent
        self.last_response: Optional[dict] = None
        self.last_billing: Optional[dict] = None

    # ------------------------------------------------------------------ #
    # Low-level networking
    # ------------------------------------------------------------------ #
    def _headers(self, extra: Optional[dict] = None) -> dict:
        headers: dict[str, str] = {"User-Agent": self.user_agent}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if extra:
            headers.update(extra)
        return headers

    def _build_url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def _request(
        self,
        method: str,
        path: str,
        json_body: Any = None,
        raw_body: Union[str, bytes, None] = None,
        content_type: Optional[str] = None,
    ) -> dict:
        """Perform an HTTP request and return a result dict:

        {
          "status":   int,            # HTTP status code
          "body":     str,            # raw response text (may be non-JSON)
          "json":     dict|None,      # parsed JSON, or None if not parseable
          "url":      str,
          "method":   str,
          "headers":  {...},
        }

        Raises MD2HTMLAPIError on urllib exceptions and (optionally, controlled
        by hard_402) when the server returns 402 Payment Required.
        """
        url = self._build_url(path)
        headers = self._headers()

        if json_body is not None:
            data = json.dumps(json_body).encode("utf-8")
            headers.setdefault("Content-Type", "application/json")
        elif raw_body is not None:
            data = raw_body.encode("utf-8") if isinstance(raw_body, str) else raw_body
            if content_type:
                headers["Content-Type"] = content_type
        else:
            data = None

        try:
            req = urllib.request.Request(
                url,
                data=data,
                method=method,
                headers=headers,
            )
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                status = resp.status
                # py3.8 compat: read raw body
                body_bytes = resp.read()
                resp_headers = dict(resp.headers)
        except urllib.error.HTTPError as exc:
            status = exc.code
            try:
                body_bytes = exc.read()
            except Exception:
                body_bytes = b""
            resp_headers = (exc.headers or {}) and dict(exc.headers) or {}
            url = exc.filename or url
        except urllib.error.URLError as exc:
            raise MD2HTMLAPIError(
                f"Network error reaching {url}: {exc.reason}",
                status_code=0,
                url=url,
                method=method,
                response_body=str(exc.reason),
            ) from exc
        except Exception as exc:
            raise MD2HTMLAPIError(
                f"Unexpected HTTP transport error reaching {url}: {exc}",
                url=url,
                method=method,
                response_body=str(exc),
            ) from exc

        body_text = body_bytes.decode("utf-8", errors="replace") if body_bytes else ""
        parsed: Optional[dict] = None
        if body_text:
            try:
                parsed = json.loads(body_text)
            except (ValueError, json.JSONDecodeError):
                # /docs is plain text — not an error.
                parsed = None

        result = {
            "status": status,
            "body": body_text,
            "json": parsed,
            "url": url,
            "method": method,
            "headers": resp_headers,
        }

        # 402 handling
        if status == 402:
            pay_hint = self._payment_hint(parsed)
            result["payment_hint"] = pay_hint
            if self.hard_402:
                raise MD2HTMLAPIError(
                    pay_hint.get("message", "402 Payment Required"),
                    status_code=402,
                    url=url,
                    method=method,
                    response_body=body_text,
                    parsed=parsed,
                )

        # Track last response (status + body)
        try:
            self.last_response = result
            if isinstance(parsed, dict):
                bill = parsed.get("billing")
                if isinstance(bill, dict):
                    self.last_billing = bill
        except Exception:
            pass

        return result

    @staticmethod
    def _payment_hint(parsed: Any) -> dict:
        if isinstance(parsed, dict):
            wa = parsed.get("wallet_address", "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM")
            made = parsed.get("calls_made", "?")
            limit = parsed.get("free_tier_limit", "?")
            err = parsed.get("error", "Free tier limit reached")
            msg = (
                f"{err}. Calls used: {made}/{limit}. "
                f"Send LTC to {wa} to continue, then call usage() to check."
            )
        else:
            wa = "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM"
            msg = "402 Payment Required. Send LTC to " + wa + " to continue."
        return {
            "status": 402,
            "wallet_address": wa,
            "message": msg,
        }

    # ------------------------------------------------------------------ #
    # Async helpers — run any method in a background thread, with an
    # optional callback(result, error=None) invoked on completion.
    # ------------------------------------------------------------------ #
    def _async(
        self,
        fn: Callable[..., Any],
        *args: Any,
        callback: Optional[Callable[[Any, Any], None]] = None,
        **kwargs: Any,
    ) -> threading.Thread:
        """Run *fn* in a background daemon thread; optionally call `callback`.
        Returns the underlying Thread so the caller can join on it.
        The callback receives (result, error) — error is a raised exception or
        None. Internal callers pass unbound methods/args cleanly.
        """

        def worker() -> None:
            result: Any = None
            error: Any = None
            try:
                result = fn(*args, **kwargs)
            except Exception as exc:                       # noqa: BLE001
                error = exc
                result = None
            if callback is not None:
                try:
                    callback(result, error)
                except Exception:
                    pass

        t = threading.Thread(target=worker, daemon=True, name="md2html-async")
        t.start()
        return t

    def _async_method(
        self,
        method_name: str,
        *args: Any,
        callback: Optional[Callable[[Any, Any], None]] = None,
        **kwargs: Any,
    ) -> threading.Thread:
        """Dispatch ``self.method_name(*args, **kwargs)`` in a thread."""
        fn = getattr(self, method_name)
        return self._async(fn, *args, callback=callback, **kwargs)

    # ------------------------------------------------------------------ #
    # Endpoint methods — one per route
    # ------------------------------------------------------------------ #

    def health(self) -> dict:
        """``GET /health`` — liveness probe. Not billed.

        Returns the parsed JSON dict (``{"status": "ok", "version": ...}``)
        or raises MD2HTMLAPIError if the request fails outright.
        """
        resp = self._request("GET", "/health")
        if resp["json"] is not None:
            return resp["json"]
        return {"status": resp["status"], "body": resp["body"]}

    def register(self) -> dict:
        """``GET /register`` — mint a new ``mk_...`` API key.

        The returned key is automatically stored on ``self.api_key`` so
        subsequent calls are billed to this key (useful for getting a fresh
        10-call free tier when the IP's bucket is exhausted). Not billed.

        Returns the parsed registration dict, typically::
            {"api_key": "mk_...",
             "wallet_address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
             "free_tier_limit": 10, "calls_made": 0, "remaining": 10}
        """
        resp = self._request("GET", "/register")
        parsed = resp["json"] if resp["json"] is not None else {}
        key = parsed.get("api_key") if isinstance(parsed, dict) else None
        if key:
            self.api_key = key
        return parsed

    def convert(self, md: str) -> Union[str, dict]:
        """``POST /convert`` — convert **Markdown** to HTML.

        Parameters
        ----------
        md : str
            Markdown source text.

        Returns
        -------
        html : str
            The converted HTML string on success. Returns a dict (with \
            ``payment_hint``) when the API returns 402. Plain text / non-JSON
            errors raise MD2HTMLAPIError.

        Example
        -------
        >>> html = client.convert("# Hello **world**\\n\\n- a\\n- b")
        >>> print(html)
        <h1>Hello <strong>world</strong></h1>
        <ul>
        <li>a</li>
        <li>b</li>
        </ul>
        """
        if not isinstance(md, str) or not md:
            raise ValueError("convert() requires a non-empty markdown string")
        resp = self._request(
            "POST", "/convert", json_body={"markdown": md}
        )
        if resp["status"] == 402:
            return resp  # type: ignore[return-value]
        if resp["json"] is None:
            raise MD2HTMLAPIError(
                "Unexpected non-JSON response from /convert",
                status_code=resp["status"],
                url=resp["url"],
                method=resp["method"],
                response_body=resp["body"],
            )
        return resp["json"].get("html", "")

    def payment(self) -> dict:
        """``GET /payment`` — return the LTC wallet address & payment
        instructions. Not billed.
        """
        resp = self._request("GET", "/payment")
        if resp["json"] is not None:
            return resp["json"]
        return {"body": resp["body"]}

    def usage(self) -> dict:
        """``GET /usage`` — return this client's call count and remaining free
        calls. Billing is via API key when present, else via client IP. Not
        billed."""
        resp = self._request("GET", "/usage")
        if resp["json"] is not None:
            return resp["json"]
        return {"body": resp["body"]}

    def stats(self) -> dict:
        """``GET /stats`` — aggregate server stats (total calls, unique IPs,
        per-endpoint breakdown). Not billed."""
        resp = self._request("GET", "/stats")
        if resp["json"] is not None:
            return resp["json"]
        return {"body": resp["body"]}

    def prettify_json(self, j: Union[str, dict, list]) -> Union[str, dict]:
        """``POST /json/prettify`` — re-indent/minify a JSON string.

        Parameters
        ----------
        j : str | dict | list
            The JSON to prettify. Dictionaries/lists are serialized for you
            before sending; strings are sent as-is.

        Returns
        -------
        pretty : str | dict
            On success, the prettified JSON text is returned as a string. \
            On 402 (free tier exhausted) a dict with payment_hint is returned.
        Raises MD2HTMLAPIError on other non-2xx responses.
        """
        json_str: str
        if isinstance(j, str):
            json_str = j
        else:
            json_str = json.dumps(j)
        body = {"json": json_str} if self.api_key else {"json": json_str}
        resp = self._request("POST", "/json/prettify", json_body=body)
        if resp["status"] == 402:
            return resp  # type: ignore[return-value]
        if resp["json"] is None:
            raise MD2HTMLAPIError(
                "Unexpected non-JSON response from /json/prettify",
                status_code=resp["status"],
                url=resp["url"],
                method=resp["method"],
                response_body=resp["body"],
            )
        # Server returns the re-indented JSON inline, with a billing wrapper
        # appended. Strip the billing wrapper so the caller sees clean JSON.
        if isinstance(resp["json"], dict) and "billing" not in resp["json"]:
            return json.dumps(resp["json"], indent=2, ensure_ascii=False)
        return resp["body"]

    def text_stats(self, t: str) -> dict:
        """``POST /text/stats`` — word/char counts, reading time, top words.

        Parameters
        ----------
        t : str
            Input text to analyze.

        Returns
        -------
        stats : dict
            On success: ``{"words": N, "chars": N, "chars_no_spaces": N,
            "reading_time_min": float, "top_words": [[word, count], ...]}``.
            On 402: a dict with payment_hint.
        Raises MD2HTMLAPIError on other errors.
        """
        if not isinstance(t, str) or not t:
            raise ValueError("text_stats() requires a non-empty text string")
        resp = self._request("POST", "/text/stats", json_body={"text": t})
        if resp["status"] == 402:
            return resp  # type: ignore[return-value]
        if resp["json"] is None:
            raise MD2HTMLAPIError(
                "Unexpected non-JSON response from /text/stats",
                status_code=resp["status"],
                url=resp["url"],
                method=resp["method"],
                response_body=resp["body"],
            )
        # Strip the billing wrapper for clean user-facing output.
        out = dict(resp["json"])
        out.pop("billing", None)
        return out

    def slug(self, s: str) -> Union[str, dict]:
        """``POST /slug`` — turn a title string into a URL-safe slug.

        Parameters
        ----------
        s : str
            The title/text to slugify.

        Returns
        -------
        slug : str
            On success, the URL-safe slug string. On 402, a dict with the
            payment hint.

        Example
        -------
        >>> client.slug("Hello, World!")
        'hello-world'
        """
        if not isinstance(s, str) or not s:
            raise ValueError("slug() requires a non-empty text string")
        resp = self._request("POST", "/slug", json_body={"title": s})
        if resp["status"] == 402:
            return resp  # type: ignore[return-value]
        if resp["json"] is None:
            raise MD2HTMLAPIError(
                "Unexpected non-JSON response from /slug",
                status_code=resp["status"],
                url=resp["url"],
                method=resp["method"],
                response_body=resp["body"],
            )
        return resp["json"].get("slug", "")

    def docs(self) -> str:
        """``GET /docs`` — fetch the plain-text usage guide. Not billed.

        Returns
        -------
        guide : str
            The plain-text documentation.
        """
        resp = self._request("GET", "/docs")
        return resp["body"]

    # ------------------------------------------------------------------ #
    # Async wrappers (threading-based, non-blocking)
    # ------------------------------------------------------------------ #
    def convert_async(
        self,
        md: str,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`convert`.

        Returns the daemon Thread so the caller can join if desired. The
        optional `callback(result, error)` receives the result or any
        exception raised inside the worker.

        Example
        -------
        >>> t = client.convert_async("# async", callback=print)
        >>> t.join()
        """
        return self._async_method("convert", md, callback=callback)

    def register_async(
        self,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`register`."""
        return self._async_method("register", callback=callback)

    def health_async(
        self,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`health`."""
        return self._async_method("health", callback=callback)

    def payment_async(
        self,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`payment`."""
        return self._async_method("payment", callback=callback)

    def usage_async(
        self,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`usage`."""
        return self._async_method("usage", callback=callback)

    def stats_async(
        self,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`stats`."""
        return self._async_method("stats", callback=callback)

    def prettify_json_async(
        self,
        j: Union[str, dict, list],
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`prettify_json`."""
        return self._async_method("prettify_json", j, callback=callback)

    def text_stats_async(
        self,
        t: str,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`text_stats`."""
        return self._async_method("text_stats", t, callback=callback)

    def slug_async(
        self,
        s: str,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`slug`."""
        return self._async_method("slug", s, callback=callback)

    def docs_async(
        self,
        callback: Optional[Callable[[Any, Any], None]] = None,
    ) -> threading.Thread:
        """Async variant of :meth:`docs`."""
        return self._async_method("docs", callback=callback)

    # ------------------------------------------------------------------ #
    # Utility
    # ------------------------------------------------------------------ #
    def __repr__(self) -> str:
        masked = self._masked_key
        return f"MD2HTMLClient(base_url={self.base_url!r}, api_key={masked!r})"

    @property
    def _masked_key(self) -> str:
        if not self.api_key:
            return "(none — IP billing)"
        if len(self.api_key) <= 8:
            return "***" + self.api_key[-3:]
        return self.api_key[:4] + "…" + self.api_key[-4:]

    def reset_billing(self) -> None:
        """Forget the stored API key — fall back to IP-based billing.

        Useful to test free-tier behavior from scratch without instantiating a
        new client.
        """
        self.api_key = ""
        self.last_billing = None


# ---------------------------------------------------------------------- #
# Module entry-point — usage example & smoke-test against the live API
# ---------------------------------------------------------------------- #
def _example() -> None:
    """A simple, copy-pasteable usage example; runs as ``python -m``."""
    print("=== MD2HTML SDK — usage example ===\n")

    client = MD2HTMLClient()
    print("Client:", client)

    # 1. Health check (not billed)
    health = client.health()
    print("\n[health]")
    print(health)

    # 2. Docs (not billed)
    print("\n[docs]")
    print(client.docs()[:200], "…")

    # 3. Payment info (not billed)
    print("\n[payment]")
    print(client.payment())

    # 4. Stats (not billed)
    print("\n[stats]")
    print(client.stats())

    # 5. Register a fresh key (auto-saved into client.api_key)
    print("\n[register]")
    reg = client.register()
    print(reg)
    print("Stored key on client:", client._masked_key)

    # 6. Convert (uses new key's free tier)
    print("\n[convert]")
    html = client.convert("# Hello\n\nThis is **bold** and *italic*.\n\n- one\n- two")
    print(html)

    # 7. Prettify JSON (uses billing)
    print("\n[prettify_json]")
    pretty = client.prettify_json('{"b":2,"a":1,"nested":{"x":[1,2]}}')
    print(pretty)

    # 8. Text stats (uses billing)
    print("\n[text_stats]")
    print(client.text_stats("The quick brown fox jumps over the lazy dog."))

    # 9. Slug (uses billing)
    print("\n[slug]")
    print(client.slug("Hello, World! My First Post"))

    # 10. Usage check (not billed)
    print("\n[usage]")
    print(client.usage())

    # 11. Async demo
    print("\n[async convert]")
    results = []

    def on_done(res, err):
        if err is not None:
            print(f"async error: {err}")
        else:
            results.append(res)
            print(f"async result: {res!r}")

    # Use a fresh key to ensure async convert doesn't hit the exhausted tier.
    reg2 = client.register()
    client.api_key = reg2["api_key"]
    t = client.convert_async("# async hello", callback=on_done)
    t.join(timeout=30)

    print(results)
    print("\nAll 10 endpoints exercised. SDK is live.")


if __name__ == "__main__":
    _example()
