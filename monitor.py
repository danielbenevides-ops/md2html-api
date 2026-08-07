"""Autonomous business product monitor (stdlib only, cron-safe).

Checks server.py on localhost:8777/health, restarts when down, logs uptime to uptime.json, and reflects liveness in ledger.
Cron (every 5 min):  */5 * * * *  cd /c/Users/pqcai/autonomous-business-product && python monitor.py"""
import json, os, subprocess, sys, time, urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.path.join(HERE, "server.py")
UPTIME_LOG = os.path.join(HERE, "uptime.json")
LEDGER = os.path.join(os.path.expanduser("~"), "AppData", "Local", "hermes", "skills", "autonomous-ai-agents", "autonomous-business", "ledger.json")
HEALTH_URL = "http://localhost:8777/health"

def check_health():
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=5) as r:
            return r.status == 200
    except Exception:
        return False

def restart_server():
    kwargs = {"cwd": HERE, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if os.name == "nt":
        kwargs["creationflags"] = 0x00000008  # DETACHED_PROCESS
    else:
        kwargs["start_new_session"] = True
    try:
        subprocess.Popen([sys.executable, SERVER], **kwargs)
        time.sleep(3)  # let new process bind before re-check
    except Exception as exc:
        print(f"[monitor] restart failed: {exc}", flush=True)

def log_uptime(up, restarted):
    entry = {"ts": datetime.now(timezone.utc).isoformat(timespec="seconds"), "up": up, "restarted": restarted}
    data = []
    if os.path.exists(UPTIME_LOG):
        try:
            with open(UPTIME_LOG, encoding="utf-8") as f:
                data = json.load(f) if os.path.getsize(UPTIME_LOG) else []
        except Exception:
            data = []
    data.append(entry)
    with open(UPTIME_LOG, "w", encoding="utf-8") as f:
        json.dump(data[-1000:], f, indent=2)  # cap history

def update_ledger(up):
    if not os.path.exists(LEDGER):
        print(f"[monitor] ledger not found: {LEDGER}", flush=True)
        return
    try:
        with open(LEDGER, encoding="utf-8") as f:
            ledger = json.load(f)
    except Exception as exc:
        print(f"[monitor] ledger read failed: {exc}", flush=True)
        return
    if ledger.get("product_live") == up:  # unchanged — avoid churn
        return
    ledger["product_live"] = bool(up)
    ledger["last_report"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    tmp = LEDGER + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ledger, f, indent=2)
    os.replace(tmp, LEDGER)

def main():
    up = check_health()
    restarted = False
    if not up:
        restart_server()
        up = check_health()
        restarted = True
    log_uptime(up, restarted)
    update_ledger(up)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"[monitor] {ts} up={up} restarted={restarted}", flush=True)

if __name__ == "__main__":
    main()
