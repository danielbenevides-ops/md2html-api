# Distribution Snippets

## 1. README badge / CTA

```md
[![Live API](https://img.shields.io/website?url=http%3A%2F%2F147.15.103.217%2Fmd2html%2Fhealth&label=Live%20API&style=for-the-badge)](http://147.15.103.217/md2html/)

[Try the HTTP API →](http://147.15.103.217/md2html/) — convert Markdown to HTML over HTTP.
```

## 2. public-apis description (73 characters)

```md
| [MD2HTML API](http://147.15.103.217/md2html/) | Convert Markdown to HTML and provide small developer utilities over HTTP. | No | No | Yes |
```

`No` in the HTTPS column is intentional: the public deployment is currently HTTP-only. The `No` auth and `Yes` CORS values reflect the live API's optional `X-API-Key` and `Access-Control-Allow-Origin: *` behavior.

## 3. Postman / OpenAPI discovery blurb

```md
Postman users can import the live [OpenAPI 3.0.3 definition](http://147.15.103.217/md2html/swagger.json) or set `base_url` to `http://147.15.103.217/md2html`. The [plain-text API guide](http://147.15.103.217/md2html/docs) lists the available endpoints and request shapes. The public deployment is currently HTTP-only; no HTTPS endpoint is advertised.
```
