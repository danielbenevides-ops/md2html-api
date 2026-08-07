"""Tests for server.py: starts the server, exercises /convert and /health,
prints PASS/FAIL for each test, and cleans up the server. Stdlib only."""
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")
HOST = "localhost"
PORT = 8777
BASE = f"http://{HOST}:{PORT}"

results = []  # (name, passed, detail)

def record(name, passed, detail=""):
    results.append((name, passed, detail))
    tag = "PASS" if passed else "FAIL"
    print(f"[{tag}] {name}" + (f" - {detail}" if detail else ""))

def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0

def wait_for_server(proc, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if proc.poll() is not None:
            return False, f"server exited early rc={proc.returncode}"
        if port_in_use(PORT):
            # Confirm HTTP responds
            try:
                urllib.request.urlopen(f"{BASE}/health", timeout=2).read()
                return True, ""
            except Exception:
                pass
        time.sleep(0.3)
    return False, "timeout waiting for port"

def stop(proc):
    if proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

def post_convert(md):
    body = json.dumps({"markdown": md}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/convert",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        status = r.status
        payload = json.loads(r.read().decode("utf-8"))
    return status, payload

def get_health():
    with urllib.request.urlopen(f"{BASE}/health", timeout=5) as r:
        status = r.status
        payload = json.loads(r.read().decode("utf-8"))
    return status, payload

def main():
    if not os.path.isfile(SERVER):
        record("server.py exists", False, f"not found at {SERVER}")
        # Print summary now since we can't run tests
        passed = sum(1 for _, p, _ in results if p)
        print(f"\n{passed}/{len(results)} tests passed")
        return 1

    # 1) Start server in background
    proc = subprocess.Popen(
        [sys.executable, SERVER],
        cwd=HERE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    try:
        # Wait for server readiness (this is itself a test)
        ok, detail = wait_for_server(proc)
        record("server starts and listens", ok, detail)
        if not ok:
            stop(proc)
            _summarize()
            return 1

        # 2 + 3) POST /convert
        md_in = "# Hello\n\n**bold** and *italic*\n\n- item1\n- item2"
        try:
            status, payload = post_convert(md_in)
            html = payload.get("html", "")
            conv_ok = (status == 200) and ("<h1>Hello</h1>" in html)
            record(
                "POST /convert returns valid HTML with <h1>Hello</h1>",
                conv_ok,
                f"status={status} html={html!r}",
            )
            # Additional structural checks for the same response
            struct_ok = all(
                s in html
                for s in (
                    "<h1>Hello</h1>",
                    "<strong>bold</strong>",
                    "<em>italic</em>",
                    "<li>item1</li>",
                    "<li>item2</li>",
                    "<ul>",
                    "</ul>",
                )
            )
            record("POST /convert full structure", struct_ok, html)
        except Exception as e:
            record("POST /convert returns valid HTML with <h1>Hello</h1>", False, f"{type(e).__name__}: {e}")
            record("POST /convert full structure", False, "convert failed above")

        # 4) GET /health
        try:
            status, payload = get_health()
            health_ok = (status == 200) and payload.get("status") == "ok"
            record("GET /health returns status ok", health_ok, f"status={status} body={payload}")
        except Exception as e:
            record("GET /health returns status ok", False, f"{type(e).__name__}: {e}")

    finally:
        # 5) Clean up server
        stop(proc)
        try:
            # Drain any output for debugging on failure
            proc.communicate(timeout=3)
        except Exception:
            pass
        record("server cleanup (terminated)", proc.poll() is not None, "")

    return _summarize()

def _summarize():
    passed = sum(1 for _, p, _ in results if p)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    if total == 0:
        return 1
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
