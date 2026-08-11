"""Live smoke tests for the public MD2HTML API contract.

The deterministic HTTP suite lives in ``test_server.py``. These checks only
verify that the deployed service exposes the documented public surface.
"""
import os
import unittest

import requests

BASE_URL = os.getenv("MD2HTML_BASE_URL", "http://147.15.103.217/md2html/").rstrip("/")
MARKDOWN = "# Hi\n\nSome **bold** `code` and a [link](https://x.io).\n\n- a\n- b\n"


class TestSuite(unittest.TestCase):
    def setUp(self):
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        register = self.session.get(f"{BASE_URL}/register", timeout=15)
        self.assertEqual(register.status_code, 200, register.text)
        self.api_key = register.json()["api_key"]
        self.headers = {"X-API-Key": self.api_key}

    def test_convert_renders_html(self):
        response = self.session.post(
            f"{BASE_URL}/convert",
            json={"markdown": MARKDOWN},
            headers=self.headers,
            timeout=15,
        )
        self.assertEqual(response.status_code, 200, response.text)
        body = response.json()
        self.assertIn("<h1>Hi</h1>", body["html"])
        self.assertIn("<strong>bold</strong>", body["html"])
        self.assertEqual(body["billing"]["status"], 200)

    def test_all_documented_get_endpoints(self):
        for path in ["health", "register", "docs", "pricing", "payment", "usage", "stats", "swagger.json"]:
            response = self.session.get(
                f"{BASE_URL}/{path}", headers=self.headers, timeout=15
            )
            self.assertLess(response.status_code, 500, f"{path}: {response.status_code}")
        spec = self.session.get(f"{BASE_URL}/swagger.json", timeout=15).json()
        self.assertEqual(spec["openapi"].split(".")[0], "3")

    def test_batch_and_utility_endpoints(self):
        batch = self.session.post(
            f"{BASE_URL}/batch",
            json={"items": ["# one", "**two**"]},
            headers=self.headers,
            timeout=15,
        )
        self.assertEqual(batch.status_code, 200, batch.text)
        self.assertEqual(batch.json()["count"], 2)

        slug = self.session.post(
            f"{BASE_URL}/slug",
            json={"title": "Café — Menus & Drinks!"},
            headers=self.headers,
            timeout=15,
        )
        self.assertEqual(slug.status_code, 200, slug.text)
        self.assertEqual(slug.json()["slug"], "cafe-menus-drinks")

    def test_empty_and_unicode_input_is_safe(self):
        empty = self.session.post(
            f"{BASE_URL}/convert",
            json={"markdown": ""},
            headers=self.headers,
            timeout=15,
        )
        self.assertEqual(empty.status_code, 200, empty.text)
        self.assertEqual(empty.json()["html"], "")

        unicode_response = self.session.post(
            f"{BASE_URL}/convert",
            json={"markdown": "Olá, 世界 🌍"},
            headers=self.headers,
            timeout=15,
        )
        self.assertEqual(unicode_response.status_code, 200, unicode_response.text)
        self.assertIn("Olá", unicode_response.json()["html"])

    def test_invalid_endpoint_is_404(self):
        response = self.session.get(f"{BASE_URL}/no_such_thing_42", timeout=15)
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
