"""Local integration tests for webhook registration and batch callbacks."""
import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

import server


class CallbackHandler(BaseHTTPRequestHandler):
    received = []
    event = threading.Event()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        self.__class__.received.append(payload)
        self.__class__.event.set()
        self.send_response(204)
        self.end_headers()

    def log_message(self, *args):
        pass


class WebhookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.callback_server = ThreadingHTTPServer(("127.0.0.1", 0), CallbackHandler)
        cls.callback_thread = threading.Thread(
            target=cls.callback_server.serve_forever, daemon=True
        )
        cls.callback_thread.start()
        cls.api_server = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        cls.api_thread = threading.Thread(
            target=cls.api_server.serve_forever, daemon=True
        )
        cls.api_thread.start()
        cls.base_url = "http://127.0.0.1:%d" % cls.api_server.server_port
        cls.callback_url = "http://127.0.0.1:%d/callback" % cls.callback_server.server_port

    @classmethod
    def tearDownClass(cls):
        cls.api_server.shutdown()
        cls.callback_server.shutdown()
        cls.api_server.server_close()
        cls.callback_server.server_close()

    def setUp(self):
        CallbackHandler.received = []
        CallbackHandler.event.clear()
        self.api_key = ""
        status, body = self.request("/register", method="GET", api_key="")
        self.assertEqual(status, 200)
        self.api_key = body["api_key"]
        with server._WEBHOOK_LOCK:
            server._webhook_registry.clear()

    def request(self, path, method="POST", payload=None, api_key=None):
        api_key = api_key or self.api_key
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path, data=data, method=method
        )
        if data is not None:
            request.add_header("Content-Type", "application/json")
        request.add_header("X-API-Key", api_key)
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read() or b"{}")
        except urllib.error.HTTPError as error:
            body = json.loads(error.read() or b"{}")
            return error.code, body

    def test_registers_callback_url(self):
        with mock.patch.object(server, "_ensure_public_webhook_host", return_value=("127.0.0.1",)):
            status, body = self.request(
                "/webhook/register", payload={"callback_url": self.callback_url}
            )
        self.assertEqual(status, 200)
        self.assertTrue(body["registered"])
        self.assertEqual(body["callback_url"], self.callback_url)

    def test_webhook_test_notifies_registered_callback(self):
        with mock.patch.object(server, "_ensure_public_webhook_host", return_value=("127.0.0.1",)):
            self.request("/webhook/register", payload={"url": self.callback_url})
            status, body = self.request("/webhook/test", payload={})
            self.assertEqual(status, 200)
            self.assertTrue(body["delivered"])
            self.assertTrue(CallbackHandler.event.wait(2))
        self.assertEqual(CallbackHandler.received[-1]["event"], "webhook.test")

    def test_batch_completion_notifies_callback_with_results(self):
        with mock.patch.object(server, "_ensure_public_webhook_host", return_value=("127.0.0.1",)):
            self.request("/webhook/register", payload={"url": self.callback_url})
            status, body = self.request(
                "/batch", payload={"items": ["# First", "## Second"]}
            )
            self.assertEqual(status, 200)
            self.assertTrue(CallbackHandler.event.wait(2))
        callback = CallbackHandler.received[-1]
        self.assertEqual(callback["event"], "batch.completed")
        self.assertEqual(callback["count"], 2)
        self.assertEqual(callback["results"], body["results"])

    def test_rejects_invalid_callback_url(self):
        status, body = self.request(
            "/webhook/register", payload={"url": "javascript:alert(1)"}
        )
        self.assertEqual(status, 400)
        self.assertIn("url", body["error"].lower())

    def test_rejects_private_callback_url(self):
        status, body = self.request(
            "/webhook/register", payload={"url": "http://127.0.0.1:9/callback"}
        )
        self.assertEqual(status, 400)
        self.assertIn("public", body["message"].lower())

    def test_webhook_test_rejects_private_override(self):
        status, body = self.request(
            "/webhook/test", payload={"callback_url": "http://127.0.0.1:9/callback"}
        )
        self.assertEqual(status, 400)
        self.assertIn("public", body["message"].lower())

    def test_delivery_uses_timeout_and_requires_2xx(self):
        response = mock.MagicMock(status=204)
        response.__enter__.return_value = response
        opener = mock.MagicMock()
        opener.open.return_value = response
        with mock.patch.object(server, "_ensure_public_webhook_host", return_value=("127.0.0.1",)), \
                mock.patch.object(server.urllib.request, "build_opener", return_value=opener):
            result = server._post_webhook("http://127.0.0.1:9/callback", {"event": "test"})
            self.assertTrue(result["delivered"])
            self.assertEqual(result["status_code"], 204)
            self.assertEqual(opener.open.call_args.kwargs["timeout"], server.WEBHOOK_TIMEOUT)
            response.status = 500
            failed = server._post_webhook("http://127.0.0.1:9/callback", {"event": "test"})
        self.assertFalse(failed["delivered"])


if __name__ == "__main__":
    unittest.main()
