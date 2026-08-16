#!/usr/bin/env python3
"""Regression test for the documented billing contract.

README documents the billing object returned by billable endpoints as
``{"status": 200, "calls_made": N, "remaining": M}`` (see the /convert,
/json/prettify, /text/stats and /slug examples). Client integrations rely on
``status`` being the integer 200 (not the string ``"ok"``) and on the
``calls_made`` key (not ``call_count``). A drift in either breaks every
integration that parses the billing object.

Offline + deterministic: starts ``server.Handler`` on an ephemeral localhost
port, using a fresh key's own free-tier bucket so the assertion is stable.
"""
from __future__ import annotations

import http.server
import json
import os
import sys
import tempfile
import threading
import unittest
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import analytics  # noqa: E402
import billing   # noqa: E402
import server    # noqa: E402


class BillingContractTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old_cwd = os.getcwd()
        os.chdir(self.tmp.name)
        self.old_usage = billing.USAGE_FILE
        self.old_log = analytics.LOG_FILE
        billing.USAGE_FILE = os.path.join(self.tmp.name, "usage.json")
        analytics.LOG_FILE = os.path.join(self.tmp.name, "analytics.json")
        server._rate_map.clear()
        server._register_map.clear()
        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.api = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)
        server._rate_map.clear()
        server._register_map.clear()
        billing.USAGE_FILE = self.old_usage
        analytics.LOG_FILE = self.old_log
        os.chdir(self.old_cwd)
        self.tmp.cleanup()

    def _req(self, path, method="GET", payload=None, headers=None):
        h = dict(headers or {})
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        if payload is not None:
            h.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(self.api + path, data=data,
                                     method=method, headers=h)
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read())

    def test_convert_billing_contract(self):
        _, reg = self._req("/register")
        self.assertIn("api_key", reg)
        key = reg["api_key"]
        status, body = self._req(
            "/convert", "POST",
            {"markdown": "# Hi **there**"},
            headers={"X-API-Key": key},
        )
        self.assertEqual(status, 200)
        self.assertIn("billing", body, "billable response must include 'billing'")
        bill = body["billing"]
        # Contract: status is the integer 200, not the string "ok".
        self.assertIsInstance(
            bill.get("status"), int,
            "billing.status must be integer 200 (README shows 200, not \"ok\")",
        )
        self.assertEqual(bill.get("status"), 200)
        # Contract: counter is exposed as 'calls_made', not 'call_count'.
        self.assertIn(
            "calls_made", bill,
            "billing must expose 'calls_made' (README shows calls_made, not call_count)",
        )
        self.assertIsInstance(bill["calls_made"], int)
        self.assertIsInstance(bill["remaining"], int)


if __name__ == "__main__":
    unittest.main()
