"""Unittest coverage for the local MD2HTML HTTP API.

The test fixture starts ``server.Handler`` on an ephemeral localhost port, so
these tests exercise real HTTP routing without depending on a running
production process or mutating the repository's usage/analytics files.
"""
from __future__ import annotations

import http.server
from concurrent.futures import ThreadPoolExecutor
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import analytics  # noqa: E402
import billing  # noqa: E402
import server  # noqa: E402

_MISSING = object()


def request(base: str, path: str, method: str = "GET", payload=_MISSING,
            *, body: bytes | str | None = None, headers: dict[str, str] | None = None):
    """Make an HTTP request and return ``(status, decoded_body, headers)``.

    HTTP errors are returned rather than raised, making assertions on 400/402/
    413/429 responses straightforward.
    """
    request_headers = dict(headers or {})
    if body is not None:
        data = body.encode("utf-8") if isinstance(body, str) else body
    elif payload is not _MISSING:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/json")
    else:
        data = None

    req = urllib.request.Request(
        base + path, data=data, method=method, headers=request_headers
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status = response.status
            raw = response.read()
            response_headers = dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
        response_headers = dict(exc.headers.items())

    text = raw.decode("utf-8", errors="replace")
    try:
        decoded = json.loads(text)
    except json.JSONDecodeError:
        decoded = text
    return status, decoded, response_headers


def auth(key: str) -> dict[str, str]:
    return {"X-API-Key": key}


class MD2HTMLAPITest(unittest.TestCase):
    """End-to-end tests against the actual stdlib HTTP Handler."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)
        self.old_usage_file = billing.USAGE_FILE
        self.old_log_file = analytics.LOG_FILE
        billing.USAGE_FILE = os.path.join(self.temp_dir.name, "usage.json")
        analytics.LOG_FILE = os.path.join(self.temp_dir.name, "analytics.json")
        server._rate_map.clear()

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.api = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        server._rate_map.clear()
        billing.USAGE_FILE = self.old_usage_file
        analytics.LOG_FILE = self.old_log_file
        os.chdir(self.old_cwd)
        self.temp_dir.cleanup()

    def key(self) -> str:
        status, body, _ = request(self.api, "/register")
        self.assertEqual(status, 200)
        self.assertIsInstance(body, dict)
        self.assertTrue(body["api_key"].startswith("mk_"))
        return body["api_key"]

    def test_health_reports_operational_server(self):
        status, body, headers = request(self.api, "/health")

        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertIsInstance(body["version"], str)
        self.assertGreaterEqual(body["uptime_seconds"], 0)
        self.assertEqual(body["port"], 8777)
        self.assertGreater(body["timestamp"], 0)
        self.assertTrue({"/convert", "/register", "/batch", "/sanitize"}.issubset(body["endpoints"]))
        self.assertEqual(headers["Access-Control-Allow-Origin"], "*")
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")

    def test_openapi_covers_all_advertised_health_endpoints(self):
        health_status, health, _ = request(self.api, "/health")
        spec_status, spec, _ = request(self.api, "/swagger.json")

        self.assertEqual(health_status, 200)
        self.assertEqual(spec_status, 200)
        self.assertEqual(spec["openapi"], "3.0.3")
        self.assertEqual(spec["info"]["version"], health["version"])
        self.assertEqual(set(health["endpoints"]), set(spec["paths"]) - {"/swagger.json"})
        self.assertIn("post", spec["paths"]["/webhook/register"])
        self.assertIn("post", spec["paths"]["/webhook/test"])

    def test_convert_basic_markdown_to_html(self):
        key = self.key()
        markdown = "# Hello\n\n**bold** and *italic*\n\n- one\n- two"
        status, body, _ = request(
            self.api, "/convert", "POST", {"markdown": markdown}, headers=auth(key)
        )

        self.assertEqual(status, 200)
        self.assertEqual(
            body["html"],
            "<h1>Hello</h1>\n\n<strong>bold</strong> and <em>italic</em>\n\n"
            "<ul>\n<li>one</li>\n<li>two</li>\n</ul>",
        )
        self.assertEqual(body["billing"]["status"], 200)
        self.assertEqual(body["billing"]["calls_made"], 1)
        self.assertEqual(body["billing"]["remaining"], billing.FREE_TIER_LIMIT - 1)

    def test_convert_accepts_plain_text_and_unicode(self):
        key = self.key()
        status, body, _ = request(
            self.api, "/convert", "POST", body="Café — привет",
            headers={**auth(key), "Content-Type": "text/plain"},
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["html"], "Café — привет")
        self.assertEqual(body["billing"]["calls_made"], 1)

    def test_convert_edge_cases_are_safe_and_bounded(self):
        key = self.key()
        status, body, _ = request(
            self.api, "/convert", "POST", {"markdown": ""}, headers=auth(key)
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["html"], "")
        self.assertIn("warning", body)

        status, body, _ = request(
            self.api, "/convert", "POST",
            {"markdown": '<script>alert("x")</script>'}, headers=auth(key),
        )
        self.assertEqual(status, 200)
        self.assertNotIn("<script>", body["html"])
        self.assertIn("&lt;script&gt;", body["html"])

        code = "```python\nprint('<x> & y')\n```"
        status, body, _ = request(
            self.api, "/convert", "POST", {"markdown": code}, headers=auth(key)
        )
        self.assertEqual(status, 200)
        self.assertIn("<pre><code>", body["html"])
        self.assertIn("&lt;x&gt; &amp; y", body["html"])

        status, body, _ = request(
            self.api, "/convert", "POST", body=b"",
            headers={**auth(key), "Content-Type": "text/plain"},
        )
        self.assertEqual(status, 400)
        self.assertEqual(body["error"], "Empty request body")

        oversized = {"markdown": "x" * (50 * 1024)}
        status, body, _ = request(
            self.api, "/convert", "POST", oversized, headers=auth(key)
        )
        self.assertEqual(status, 413)
        self.assertEqual(body["error"], "Markdown input too large")
        self.assertEqual(body["max_bytes"], 50 * 1024)

    def test_register_mints_independent_free_tier_key(self):
        first_status, first, _ = request(self.api, "/register")
        second_status, second, _ = request(self.api, "/register")

        self.assertEqual(first_status, second_status, 200)
        self.assertTrue(first["api_key"].startswith("mk_"))
        self.assertEqual(len(first["api_key"]), 35)
        self.assertNotEqual(first["api_key"], second["api_key"])
        self.assertEqual(first["calls_made"], 0)
        self.assertEqual(first["remaining"], billing.FREE_TIER_LIMIT)
        self.assertEqual(first["free_tier_limit"], billing.FREE_TIER_LIMIT)
        self.assertTrue(first["wallet_address"])

    def test_batch_converts_items_and_bills_per_item(self):
        key = self.key()
        status, body, _ = request(
            self.api, "/batch", "POST", {"items": ["# A", "**bold**", 42]},
            headers=auth(key),
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["count"], 3)
        self.assertEqual(len(body["results"]), 3)
        self.assertEqual(body["results"][0], "<h1>A</h1>")
        self.assertIn("<strong>bold</strong>", body["results"][1])
        self.assertEqual(body["results"][2], "42")
        self.assertEqual(body["billing"]["calls_made"], 3)
        self.assertEqual(body["billing"]["remaining"], billing.FREE_TIER_LIMIT - 3)

    def test_batch_rejects_invalid_payloads(self):
        cases = [
            ({}, 400, "Missing 'items' field"),
            ({"items": "not-a-list"}, 400, "must be a list"),
            ({"items": []}, 400, "Empty 'items' list"),
            ({"items": ["ok", None]}, 400, "Item 1 is null"),
            ({"items": ["x"] * 51}, 413, "Too many items"),
        ]
        key = self.key()
        for payload, expected_status, error_fragment in cases:
            with self.subTest(payload=payload):
                status, body, _ = request(
                    self.api, "/batch", "POST", payload, headers=auth(key)
                )
                self.assertEqual(status, expected_status)
                self.assertIn(error_fragment, body["error"])

    def test_sanitize_escapes_raw_html_before_conversion(self):
        key = self.key()
        markdown = "# Hi <script>alert(1)</script> **bold**"
        status, body, _ = request(
            self.api, "/sanitize", "POST", {"markdown": markdown}, headers=auth(key)
        )

        self.assertEqual(status, 200)
        self.assertTrue(body["sanitized"])
        self.assertNotIn("<script", body["html"])
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", body["html"])
        self.assertIn("<strong>bold</strong>", body["html"])
        self.assertEqual(body["billing"]["calls_made"], 1)

    def test_json_prettify_round_trips_and_rejects_malformed_json(self):
        key = self.key()
        compact = '{"b":2,"a":1,"nested":{"x":[1,2]}}'
        status, body, _ = request(
            self.api, "/json/prettify", "POST", {"json": compact}, headers=auth(key)
        )

        self.assertEqual(status, 200)
        self.assertEqual(
            {k: v for k, v in body.items() if k != "billing"}, json.loads(compact)
        )
        self.assertEqual(body["billing"]["calls_made"], 1)

        status, error, _ = request(
            self.api, "/json/prettify", "POST", {"json": '{"broken":]'},
            headers=auth(key),
        )
        self.assertEqual(status, 400)
        self.assertEqual(error["error"], "Bad input")
        self.assertIn("Invalid JSON", error["message"])

    def test_text_stats_reports_counts_reading_time_and_top_words(self):
        key = self.key()
        text = "The quick brown fox. The fox jumps over the lazy dog!"
        status, body, _ = request(
            self.api, "/text/stats", "POST", {"text": text}, headers=auth(key)
        )

        words = text.split()
        self.assertEqual(status, 200)
        self.assertEqual(body["words"], len(words))
        self.assertEqual(body["chars"], len(text))
        self.assertEqual(body["chars_no_spaces"], len("".join(words)))
        self.assertEqual(body["reading_time_min"], round(len(words) / 200, 2))
        top_words = dict(body["top_words"])
        self.assertEqual(top_words["the"], 3)
        self.assertEqual(top_words["fox"], 2)
        self.assertEqual(body["billing"]["calls_made"], 1)

    def test_slug_normalizes_unicode_punctuation_and_whitespace(self):
        key = self.key()
        status, body, _ = request(
            self.api, "/slug", "POST", {"title": "  Café — Menus & Drinks!  "},
            headers=auth(key),
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["slug"], "cafe-menus-drinks")
        self.assertEqual(body["billing"]["calls_made"], 1)

        status, body, _ = request(
            self.api, "/slug", "POST", {"title": "!!!---###"}, headers=auth(key)
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["slug"], "")

    def test_rate_limit_returns_429_after_configured_window_quota(self):
        self.key()
        # Registration itself is a GET and consumes one rate-limit slot; clear
        # it so this test exercises exactly RATE_LIMIT_MAX requests.
        server._rate_map.clear()

        for _ in range(server.RATE_LIMIT_MAX):
            status, body, _ = request(self.api, "/health")
            self.assertEqual(status, 200, body)

        status, body, _ = request(self.api, "/health")
        self.assertEqual(status, 429)
        self.assertEqual(body["error"], "Rate limit exceeded")
        self.assertEqual(body["retry_after"], server.RATE_LIMIT_WINDOW)

    def test_free_tier_exhaustion_returns_402_with_payment_details(self):
        key = self.key()
        for expected_call in range(1, billing.FREE_TIER_LIMIT + 1):
            status, body, _ = request(
                self.api, "/convert", "POST", {"markdown": f"call {expected_call}"},
                headers=auth(key),
            )
            self.assertEqual(status, 200)
            self.assertEqual(body["billing"]["calls_made"], expected_call)
            self.assertEqual(
                body["billing"]["remaining"], billing.FREE_TIER_LIMIT - expected_call
            )

        status, body, _ = request(
            self.api, "/convert", "POST", {"markdown": "over free tier"},
            headers=auth(key),
        )
        self.assertEqual(status, 402)
        self.assertEqual(body["status"], 402)
        self.assertEqual(body["error"], "Payment Required")
        self.assertEqual(body["calls_made"], billing.FREE_TIER_LIMIT + 1)
        self.assertEqual(body["free_tier_limit"], billing.FREE_TIER_LIMIT)
        self.assertTrue(body["wallet_address"])

    def test_concurrent_calls_do_not_oversell_free_tier(self):
        key = self.key()

        def call(index):
            return request(
                self.api, "/convert", "POST", {"markdown": f"parallel {index}"},
                headers=auth(key),
            )

        with ThreadPoolExecutor(max_workers=20) as pool:
            responses = list(pool.map(call, range(20)))

        statuses = [status for status, _, _ in responses]
        self.assertEqual(statuses.count(200), billing.FREE_TIER_LIMIT)
        self.assertEqual(statuses.count(402), 20 - billing.FREE_TIER_LIMIT)
        self.assertEqual(
            billing.check_usage(key)["call_count"],
            20,
        )

    def test_minify_empty_input_is_billed_once(self):
        key = self.key()
        status, body, _ = request(
            self.api, "/minify", "POST", {"code": ""}, headers=auth(key)
        )

        self.assertEqual(status, 200)
        self.assertEqual(body["warning"], "Empty input — nothing to minify.")
        self.assertEqual(body["billing"]["status"], 200)
        self.assertEqual(body["billing"]["calls_made"], 1)

    def test_batch_returns_partial_results_when_billing_expires_mid_request(self):
        key = self.key()
        for index in range(billing.FREE_TIER_LIMIT - 1):
            status, _, _ = request(
                self.api, "/convert", "POST", {"markdown": str(index)},
                headers=auth(key),
            )
            self.assertEqual(status, 200)

        status, body, _ = request(
            self.api, "/batch", "POST",
            {"items": ["# allowed", "blocked", "also blocked"]},
            headers=auth(key),
        )
        self.assertEqual(status, 402)
        self.assertEqual(body["error"], "Payment Required")
        self.assertEqual(body["partial_results"], ["<h1>allowed</h1>"])
        self.assertEqual(body["billing"]["status"], 402)
        self.assertEqual(body["billing"]["calls_made"], billing.FREE_TIER_LIMIT + 1)
        self.assertTrue(body["wallet_address"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
