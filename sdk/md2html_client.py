"""Small, dependency-free Python client for the MD2HTML API.

The public API is intentionally tiny: convert Markdown, convert batches, create
an API key, inspect usage, pretty-print JSON, and calculate text statistics.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Union

__version__ = "0.1.0"
DEFAULT_BASE_URL = "http://147.15.103.217/md2html"


class Md2HTMLAPIError(RuntimeError):
    """Raised when the API or the HTTP transport returns an error."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 0,
        url: str = "",
        response_body: str = "",
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.url = url
        self.response_body = response_body


class Md2HTMLClient:
    """Client for the MD2HTML HTTP API.

    Args:
        base_url: API root. Defaults to the hosted MD2HTML service.
        api_key: Optional ``mk_...`` key sent as ``X-API-Key``.
        timeout: Per-request timeout in seconds.
    """

    def __init__(
        self,
        base_url: str = DEFAULT_BASE_URL,
        api_key: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("base_url must be a non-empty URL")
        if timeout <= 0:
            raise ValueError("timeout must be greater than zero")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self.timeout = float(timeout)
        self.last_response: Optional[Any] = None

    def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send one JSON request and return its decoded response body."""
        url = self.base_url + "/" + path.lstrip("/")
        headers = {
            "Accept": "application/json",
            "User-Agent": "md2html-python-sdk/" + __version__,
        }
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self.api_key:
            headers["X-API-Key"] = self.api_key

        request = urllib.request.Request(
            url, data=body, headers=headers, method=method.upper()
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                status = response.status
                raw = response.read()
        except urllib.error.HTTPError as error:
            raw = error.read()
            text = raw.decode("utf-8", errors="replace")
            raise Md2HTMLAPIError(
                "MD2HTML API returned HTTP {}".format(error.code),
                status_code=error.code,
                url=url,
                response_body=text,
            ) from error
        except urllib.error.URLError as error:
            raise Md2HTMLAPIError(
                "Could not reach MD2HTML API: {}".format(error.reason),
                url=url,
            ) from error
        except OSError as error:
            raise Md2HTMLAPIError(
                "Could not reach MD2HTML API: {}".format(error),
                url=url,
            ) from error

        text = raw.decode("utf-8", errors="replace")
        if status >= 400:
            raise Md2HTMLAPIError(
                "MD2HTML API returned HTTP {}".format(status),
                status_code=status,
                url=url,
                response_body=text,
            )
        if not text.strip():
            decoded: Any = None
        else:
            try:
                decoded = json.loads(text)
            except ValueError:
                decoded = text
        self.last_response = decoded
        return decoded

    @staticmethod
    def _require_text(value: Any, name: str) -> str:
        if not isinstance(value, str):
            raise TypeError("{} must be a string".format(name))
        return value

    @staticmethod
    def _require_object(response: Any, endpoint: str) -> Dict[str, Any]:
        if not isinstance(response, dict):
            raise Md2HTMLAPIError(
                "{} returned an unexpected response".format(endpoint),
                response_body=repr(response),
            )
        return response

    def convert(self, md: str) -> str:
        """Convert one Markdown document and return its HTML string."""
        md = self._require_text(md, "md")
        response = self._require_object(
            self._request("POST", "/convert", {"markdown": md}), "/convert"
        )
        if "html" not in response:
            raise Md2HTMLAPIError(
                "/convert response did not include 'html'",
                response_body=json.dumps(response),
            )
        return str(response["html"])

    def batch(self, items: Iterable[str]) -> List[str]:
        """Convert up to 50 Markdown documents and return HTML strings."""
        if isinstance(items, (str, bytes)):
            raise TypeError("items must be an iterable of Markdown strings")
        values = list(items)
        if not values:
            raise ValueError("items must contain at least one Markdown string")
        if len(values) > 50:
            raise ValueError("items cannot contain more than 50 documents")
        for item in values:
            self._require_text(item, "each item")

        response = self._request("POST", "/batch", {"items": values})
        if isinstance(response, list):
            return [str(item) for item in response]
        response_object = self._require_object(response, "/batch")
        results = response_object.get("results")
        if not isinstance(results, list):
            raise Md2HTMLAPIError(
                "/batch response did not include a results list",
                response_body=json.dumps(response_object),
            )
        return [str(item) for item in results]

    def register(self, email: str) -> Dict[str, Any]:
        """Register an email and return the API key response.

        Current hosted deployments historically exposed ``GET /register``
        without an email. The requested POST form is attempted first; a 404 or
        405 transparently falls back to that legacy endpoint.
        """
        email = self._require_text(email, "email")
        if not email.strip():
            raise ValueError("email must not be empty")
        try:
            response = self._request("POST", "/register", {"email": email})
        except Md2HTMLAPIError as error:
            if error.status_code not in (404, 405):
                raise
            response = self._request("GET", "/register")
        response_object = self._require_object(response, "/register")
        key = response_object.get("api_key")
        if isinstance(key, str) and key:
            self.api_key = key
        return response_object

    def get_usage(self) -> Dict[str, Any]:
        """Return usage and remaining free-tier calls."""
        return self._require_object(self._request("GET", "/usage"), "/usage")

    def prettify_json(self, data: Union[str, Dict[str, Any], List[Any]]) -> str:
        """Pretty-print JSON data and return the formatted JSON string."""
        if isinstance(data, str):
            json_text = data
        else:
            try:
                json_text = json.dumps(data, ensure_ascii=False)
            except (TypeError, ValueError) as error:
                raise TypeError("data must be JSON-serializable") from error
        response = self._request("POST", "/json/prettify", {"json": json_text})
        if isinstance(response, str):
            return response
        response_object = self._require_object(response, "/json/prettify")
        prettified = response_object.get("prettified")
        if isinstance(prettified, str):
            return prettified
        # A compatible self-hosted API may return the decoded JSON object.
        without_billing = dict(response_object)
        without_billing.pop("billing", None)
        return json.dumps(without_billing, indent=2, ensure_ascii=False)

    def text_stats(self, text: str) -> Dict[str, Any]:
        """Return word, character, reading-time, and top-word statistics."""
        text = self._require_text(text, "text")
        response = self._require_object(
            self._request("POST", "/text/stats", {"text": text}), "/text/stats"
        )
        result = dict(response)
        result.pop("billing", None)
        return result

    # Friendly aliases used by earlier versions of the SDK.
    usage = get_usage

    def __repr__(self) -> str:
        key = "set" if self.api_key else "unset"
        return "Md2HTMLClient(base_url={!r}, api_key={})".format(self.base_url, key)


# Backwards-compatible names for the first SDK draft.
MD2HTMLClient = Md2HTMLClient
MD2HTMLAPIError = Md2HTMLAPIError

__all__ = [
    "Md2HTMLClient",
    "Md2HTMLAPIError",
    "MD2HTMLClient",
    "MD2HTMLAPIError",
]
