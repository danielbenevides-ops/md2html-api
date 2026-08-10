import os, unittest, requests
B = os.getenv("MD2HTML_BASE_URL", "http://147.15.103.217/md2html/")
MD = "# Hi\n\nSome **bold** `code` and a [link](https://x.io).\n\n* a\n* b\n"

class TestSuite(unittest.TestCase):
    def setUp(self):
        self.s = requests.Session()

    def test_page_renders_html(self):
        r = self.s.post(B, data={"page": MD}); self.assertEqual(r.status_code, 200)
        self.assertIn("<html", r.text.lower())

    def test_all_get_endpoints(self):
        for p in ["debug", "openapi.json", "help", "stylesheet", "health", "zones", "invalid_shorthand"]:
            r = self.s.get(B + p)
            self.assertLess(r.status_code, 500, f"{p}: {r.status_code}")
        self.assertEqual(self.s.get(B + "openapi.json").json()["openapi"].split(".")[0], "3")

    def test_set_default_page(self):
        r = self.s.post(B + "set_default_page", data={"page": MD})
        self.assertLess(r.status_code, 500)

    def test_expand_templates(self):
        r = self.s.post(B + "expand_templates", json={"page": "{{#div}}x{{/div}}"})
        self.assertLess(r.status_code, 500)

    def test_edge_empty_and_unicode(self):
        self.assertLess(self.s.post(B, data={"page": ""}).status_code, 500)
        big = ("# x\n\nü \n" * 200).encode()
        self.assertLess(self.s.post(B, data={"page": big}).status_code, 500)

    def test_invalid_endpoint_404(self):
        self.assertEqual(self.s.get(B + "no_such_thing_42").status_code, 404)

if __name__ == "__main__":
    unittest.main()
