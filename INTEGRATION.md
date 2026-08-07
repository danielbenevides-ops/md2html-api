# billing.py ↔ server.py Integration Guide

Stdlib only. Three small patches to `server.py`; one `.env` line.

## 1. Import billing & read wallet from env (top of server.py)
```python
import http.server, json, re, os
import billing
billing.CRYPTO_WALLET = os.getenv("PAYMENT_WALLET", billing.CRYPTO_WALLET)
billing.FREE_TIER_LIMIT = int(os.getenv("FREE_TIER_LIMIT", billing.FREE_TIER_LIMIT))
```

## 2. Billing check inside `do_POST` `/convert` (before converting)
```python
if self.path != "/convert":
    self.send(404, json.dumps({"error": "not found"})); return
api_key = self.client_address[0]            # IP as client key
usage = billing.record_call(api_key)
if usage["status"] == 402:
    self.send(402, json.dumps(usage)); return  # Payment Required
# ...existing markdown conversion code unchanged...
```

## 3. Add `/payment` & `/usage` endpoints in `do_GET`
```python
elif self.path == "/payment":
    self.send(200, json.dumps({
        "wallet_address": billing.CRYPTO_WALLET,
        "currency": "USDT (ERC-20)",
        "notes": "Send any amount; email tx hash to reset usage."}))
elif self.path == "/usage":
    u = billing.check_usage(self.client_address[0])
    self.send(200, json.dumps({
        "client": self.client_address[0],
        "calls_made": u.get("call_count", 0),
        "free_tier_limit": billing.FREE_TIER_LIMIT,
        "remaining": max(billing.FREE_TIER_LIMIT - u.get("call_count", 0), 0)}))
```

## 4. Set wallet address in `.env`
```env
# .env  (load with `export $(xargs <.env)` before `python server.py`, or use dotenv)
PAYMENT_WALLET=0xYourCryptoWalletAddressHere
FREE_TIER_LIMIT=10
```
Override the hardcoded `CRYPTO_WALLET` in `billing.py` line 10 by setting `PAYMENT_WALLET`. Python stdlib has no `.env` loader; either `export` the vars in your start script or add a 4-line loader:
```python
# optional .env loader (put before importing billing)
for line in open(".env"):
    k, _, v = line.strip().partition("=")
    if k and not k.startswith("#"): os.environ.setdefault(k, v)
```

## Verify
```bash
python server.py &
curl localhost:8777/convert -d '# Hello'   # 200, increments usage
curl localhost:8777/usage                   # shows remaining
curl localhost:8777/payment                 # shows wallet
```
