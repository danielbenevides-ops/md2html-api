"""Analytics tracking for autonomous-business API usage. Stdlib only."""
import json, os
from collections import Counter
from datetime import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analytics.json")


def log_call(endpoint, client_ip, status, latency, timestamp=None):
    """Append a single API-call record to analytics.json."""
    entry = {
        "timestamp": timestamp or datetime.utcnow().isoformat() + "Z",
        "endpoint": endpoint,
        "client_ip": client_ip,
        "status": status,
        "latency": round(float(latency), 3),
    }
    records = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as fh:
                records = json.load(fh)
        except (json.JSONDecodeError, ValueError):
            records = []
    records.append(entry)
    with open(LOG_FILE, "w") as fh:
        json.dump(records, fh, indent=2)
    return entry


def _load_records():
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, ValueError):
        return []


def get_stats():
    """Return aggregate stats dict from logged records."""
    records = _load_records()
    if not records:
        return {"total_calls": 0, "unique_ips": 0,
                "calls_by_endpoint": {}, "avg_latency": 0.0}
    by_ep = Counter(r["endpoint"] for r in records)
    ips = set(r["client_ip"] for r in records)
    avg = sum(r["latency"] for r in records) / len(records)
    return {
        "total_calls": len(records),
        "unique_ips": len(ips),
        "calls_by_endpoint": dict(by_ep),
        "avg_latency": round(avg, 3),
    }


def daily_report(target_date=None):
    """Return a human-readable summary string for a given date (YYYY-MM-DD).
    Defaults to today's UTC date."""
    target = target_date or datetime.utcnow().date().isoformat()
    records = [r for r in _load_records() if r["timestamp"].startswith(target)]
    if not records:
        return f"Daily report {target}: No API calls logged."
    by_ep = Counter(r["endpoint"] for r in records)
    ips = set(r["client_ip"] for r in records)
    avg = sum(r["latency"] for r in records) / len(records)
    lines = [
        f"=== Daily Analytics Report — {target} ===",
        f"Total calls : {len(records)}",
        f"Unique IPs  : {len(ips)}",
        f"Avg latency : {avg:.3f}s",
        "Calls by endpoint:",
    ]
    lines += [f"  {ep}: {cnt}" for ep, cnt in by_ep.items()]
    return "\n".join(lines)


if __name__ == "__main__":
    # Simple smoke test
    test_file = LOG_FILE + ".test"
    orig = LOG_FILE
    globals()["LOG_FILE"] = test_file
    if os.path.exists(test_file):
        os.remove(test_file)
    log_call("/health", "127.0.0.1", 200, 0.012)
    log_call("/chat", "10.0.0.5", 200, 0.087)
    log_call("/health", "127.0.0.1", 200, 0.009)
    stats = get_stats()
    assert stats["total_calls"] == 3, f"expected 3, got {stats['total_calls']}"
    assert stats["unique_ips"] == 2, f"expected 2, got {stats['unique_ips']}"
    assert stats["calls_by_endpoint"]["/health"] == 2
    assert stats["calls_by_endpoint"]["/chat"] == 1
    rep = daily_report()
    assert "Total calls : 3" in rep
    os.remove(test_file)
    globals()["LOG_FILE"] = orig
    print("All analytics.py tests passed.")
    print(json.dumps(stats, indent=2))
    print(rep)
