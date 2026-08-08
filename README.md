# MD2HTML API

A markdown-to-HTML conversion API with a freemium model. 10 free calls, then pay via Litecoin.

**Public API URL:** http://147.15.103.217/md2html/

## Getting Started

1. Register for an API key:
   ```bash
   curl -X POST http://147.15.103.217/md2html/register \
     -H "Content-Type: application/json" \
     -d '{"email":"you@example.com"}'
   ```
2. Use your API key in the `X-API-Key` header for all requests.
3. You get 10 free calls. After that, requests return `402 Payment Required`.
4. Pay by sending LTC to the wallet below; then call `/payment` to confirm.

## Pricing

| Tier | Cost |
|------|------|
| First 10 calls | Free |
| After 10 calls | 402 + LTC payment |

**LTC Wallet:** `Las7JLihEnYvACUt4jgxqcFcsFZrD3RgVM`

## Endpoints

### 1. Health Check
```bash
curl http://147.15.103.217/md2html/health
```

### 2. Register
```bash
curl -X POST http://147.15.103.217/md2html/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com"}'
```

### 3. Convert Markdown to HTML
```bash
curl -X POST http://147.15.103.217/md2html/convert \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"markdown":"# Hello World"}'
```

### 4. JSON Prettify
```bash
curl -X POST http://147.15.103.217/md2html/json/prettify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"json":"{\"key\":\"value\"}"}'
```

### 5. Text Stats
```bash
curl -X POST http://147.15.103.217/md2html/text/stats \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"text":"The quick brown fox jumps over the lazy dog."}'
```

### 6. Slug Generator
```bash
curl -X POST http://147.15.103.217/md2html/slug \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"text":"Hello World This Is A Title"}'
```

### 7. Docs
```bash
curl http://147.15.103.217/md2html/docs
```

### 8. Payment
```bash
curl -X POST http://147.15.103.217/md2html/payment \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"txid":"YOUR_LITECOIN_TX_ID","amount":0.01}'
```

### 9. Usage
```bash
curl http://147.15.103.217/md2html/usage \
  -H "X-API-Key: YOUR_API_KEY"
```

### 10. Stats
```bash
curl http://147.15.103.217/md2html/stats \
  -H "X-API-Key: YOUR_API_KEY"
```

## Repository

GitHub: [dcn13l/md2html-api](https://github.com/dcn13l/md2html-api)

## License

MIT
