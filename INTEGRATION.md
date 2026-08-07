# Integration & Payment Guide — md2html LTC API

Stdlib-only Python server (`server.py`) on **port 8777**.
Currency: **Litecoin (LTC)**. Wallet: `Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM` (loaded from `wallet.json`, env override `PAYMENT_WALLET`).
Free tier: 10 calls per IP. After that: HTTP `402 Payment Required` + wallet address.

## External user payment flow (manual / honor-system)

> ⚠️ **No automatic verification yet.** Payment is on the honor system — the server
> does not watch the LTC chain. Operators must manually reset usage after confirming
> a transaction. See *Future: automatic verification* below.

**As an external user, to keep calling the API past the free tier:**

1. **Hit your first 10 free calls.** Any `POST /convert` (or `/json/prettify`,
   `/text/stats`, `/slug`) works without paying. Billing is keyed by your IP.
   ```bash
   curl -X POST http://<host>:8777/convert \
        -H "Content-Type: application/json" \
        -d '{"markdown":"# Hello **world**"}'
   ```
2. **Check your usage** to see how close you are to the limit:
   ```bash
   curl http://<host>:8777/usage
   # {"calls_made": 9, "free_tier_limit": 10, "remaining": 1, ...}
   ```
3. **Get the wallet address** from the payment endpoint:
   ```bash
   curl http://<host>:8777/payment
   # {"wallet_address":"Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
   #  "currency":"LTC",
   #  "message":"Send any amount of Litecoin to this address..."}
   ```
4. **Send LTC** from any wallet to that address. Amount is unspecified
   ("any amount") at this stage — pick what you think the usage is worth.
   Save your **transaction hash (txid)**; you'll send it to the operator.
5. **Send the txid to the operator** (email/DM, out-of-band). The operator
   checks the transaction on a public LTC explorer such as
   `https://chain.so/address/Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`, then runs
   `billing.reset_usage("<your IP>")` (or restarts the server) to clear your
   free-tier counter.
6. **Call again.** Once your counter is reset, `/convert` returns `200` and
   you get another free tier block. Repeat steps 3–6 as needed.

> Note: there is currently **no `/unlock` endpoint** on the server. The
> "unlock" step is the operator's manual `reset_usage()` call. When a real
> `/unlock` endpoint is added, the flow will become:
> `POST /unlock {"txid":"..."}` → server verifies → counter cleared.

## API key registration

**There is currently no `/register` endpoint and no API-key system.**
Billing is keyed by client IP address via `billing.record_call(ip)`.
A future `/register` endpoint could issue API keys (replacing IP-based
identity) so users get stable identity across IP changes and operators can
attach paid credit to a key. Not yet implemented.

## Server internals — integration notes for operators

### Wallet address source
`server.py` reads `wallet.json` (same dir as the script), falling back to
the hardcoded constant `Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`:
```python
_WALLET_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallet.json")
WALLET_ADDRESS = json.load(open(_WALLET_FILE)).get("address", "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM")
```
To change the address, edit `wallet.json` or set `PAYMENT_WALLET` in env.

### Billing check inside `do_POST` (every billable path)
```python
bill = record_call(client_ip)
if bill.get("status") == 402:
    self.send(402, json.dumps(bill))   # Payment Required + wallet address
    return
```
`record_call()` (in `billing.py`) increments the IP's call count; once it
exceeds `FREE_TIER_LIMIT` (default `10`), subsequent calls return `402`
with a body containing the wallet address and instructions.

### `/payment` endpoint (`do_GET`)
```python
elif self.path == "/payment":
    self.send(200, json.dumps({
        "wallet_address": WALLET_ADDRESS,
        "currency": "LTC",
        "message": "Send any amount of Litecoin to this address..."
    }))
```

### `/usage` endpoint (`do_GET`)
```python
elif self.path == "/usage":
    usage = check_usage(client_ip)
    self.send(200, json.dumps({
        "client": client_ip,
        "calls_made": usage.get("call_count", 0),
        "free_tier_limit": FREE_TIER_LIMIT,
        "remaining": max(FREE_TIER_LIMIT - usage.get("call_count", 0), 0)
    }))
```

### Manual reset (operator action, no endpoint)
`billing.reset_usage(ip)` wipes the IP's counter from `usage.json`.
Today this is the *only* way to clear usage — there is no `/unlock`
endpoint, so clearing is fully honor-system.

### Local verification
```bash
python server.py &
curl localhost:8777/convert -d '# Hello'        # 200, increments usage
curl localhost:8777/usage                        # shows remaining
curl localhost:8777/payment                      # shows LTC wallet
# run 11 times to trigger 402:
for i in $(seq 1 12); do curl -s localhost:8777/convert -d '## x'>/dev/null; done
curl localhost:8777/usage                        # remaining: 0
curl localhost:8777/convert -d '## x'           # 402 + wallet address
```

## Future: automatic verification via BlockCypher webhook

No chain-watching today. The plan: register a webhook with the
[BlockCypher LTC API](https://www.blockcypher.com/dev/litecoin/) so the
server receives a push when LTC lands at the wallet address, then auto-reset
the paying IP. Sketch:

1. **Register a webhook** with BlockCypher for our address:
   ```bash
   curl -X POST https://api.blockcypher.com/v1/ltc/main/hooks \
        -H "Content-Type: application/json" \
        -d '{
          "event": "tx-confirmation",
          "address": "Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM",
          "url": "https://<our-host>/webhook/blockcypher",
          "token": "<BLOCKCYPHER_TOKEN>",
          "confirmations": 3
        }'
   ```
   BlockCypher will POST to `/webhook/blockcypher` on each confirmation.

2. **Add a `/unlock` endpoint** with optional manual fallback:
   ```python
   # do_POST
   if path == "/unlock":
       raw, status, err = self._read_body()
       txid = json.loads(raw).get("txid")
       # verify txid against the in-memory webhook log, OR do an on-demand lookup:
       #   GET https://api.blockcypher.com/v1/ltc/main/txs/<txid>?token=...
       # check that one of its vout addresses == WALLET_ADDRESS
       # then call reset_usage(client_ip) and return 200.
   ```

3. **Add a `/webhook/blockcypher` endpoint** (verify the BlockCypher
   signature, persist the txid + sending metadata, and call `reset_usage`
   for the IP associated with that txid — requires the user to attach their
   IP or a code to the LTC payment, since LTC has no native memo; e.g.
   sub-penny distinct-amount-per-user scheme).

4. **Replace honor-system `reset_usage` calls** with webhook-driven ones once
   3+ confirmations are reliable. Keep the manual `/unlock` as a fallback
   for users whose webhook never fires.

Migration note: switching from IP-keyed billing to API keys (via a future
`/register` endpoint) makes step 3 deterministic — we'd map a confirmed
txid to a registered key rather than guessing which IP paid.

## Changelog
- Server now uses **LTC** (not USDT). `wallet.json`-driven address.
- `/-register` for API keys: **not yet implemented** (future).
- `/unlock`: **not yet implemented** (manual `reset_usage` only today).
- Automatic LTC verification: **planned, not built**.
