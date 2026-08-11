import json
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from md2html_client import Md2HTMLAPIError, Md2HTMLClient


class Handler(BaseHTTPRequestHandler):
    requests = []

    def log_message(self, *_args):
        pass

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length) or b"{}")
        self.requests.append((self.command, self.path, payload))
        if self.path == "/convert":
            response = {"html": "<h1>Hi</h1>", "billing": {"remaining": 9}}
        elif self.path == "/batch":
            response = {"results": ["<h1>A</h1>", "<h1>B</h1>"], "count": 2}
        elif self.path == "/json/prettify":
            response = {"prettified": '{\n  "a": 1\n}'}
        elif self.path == "/register":
            response = {"api_key": "mk_test", "email": payload["email"]}
        elif self.path == "/text/stats":
            response = {"words": 2, "chars": 3, "billing": {"remaining": 8}}
        else:
            self.send_error(404)
            return
        self._send(200, response)

    def do_GET(self):
        self.requests.append((self.command, self.path, None))
        if self.path == "/usage":
            self._send(200, {"calls_made": 1, "remaining": 9})
        elif self.path == "/register":
            self._send(200, {"api_key": "mk_fallback"})
        else:
            self.send_error(404)

    def _send(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ClientTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Handler.requests = []
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.client = Md2HTMLClient(
            f"http://127.0.0.1:{cls.server.server_port}"
        )

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()

    def test_convert_posts_markdown_and_returns_html(self):
        self.assertEqual(self.client.convert("# Hi"), "<h1>Hi</h1>")
        self.assertEqual(
            Handler.requests[-1], ("POST", "/convert", {"markdown": "# Hi"})
        )

    def test_batch_returns_html_results(self):
        self.assertEqual(
            self.client.batch(["# A", "# B"]), ["<h1>A</h1>", "<h1>B</h1>"]
        )
        self.assertEqual(
            Handler.requests[-1],
            ("POST", "/batch", {"items": ["# A", "# B"]}),
        )

    def test_register_sends_email_and_stores_api_key(self):
        result = self.client.register("dev@example.com")
        self.assertEqual(result["email"], "dev@example.com")
        self.assertEqual(self.client.api_key, "mk_test")
        self.assertEqual(
            Handler.requests[-1],
            ("POST", "/register", {"email": "dev@example.com"}),
        )

    def test_get_usage_and_helpers(self):
        self.assertEqual(self.client.get_usage()["remaining"], 9)
        self.assertEqual(self.client.prettify_json({"a": 1}), '{\n  "a": 1\n}')
        self.assertEqual(self.client.text_stats("a b")["words"], 2)

    def test_http_errors_expose_status(self):
        with self.assertRaises(Md2HTMLAPIError) as context:
            self.client._request("GET", "/missing")
        self.assertEqual(context.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
