# HTTPS deployment

Production base URL: `https://147.15.103.217.sslip.io/md2html`

The `sslip.io` hostname resolves to the Oracle public IP. Let's Encrypt provides the certificate; nginx terminates TLS and proxies `/md2html/` to `127.0.0.1:8777`.

## Nginx

Add [`deploy/nginx-md2html-location.conf`](deploy/nginx-md2html-location.conf) inside the TLS `server` block for `147.15.103.217.sslip.io`, then validate before reload:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Keep backups outside `/etc/nginx/sites-enabled`; nginx loads every file in that directory and a backup there can create duplicate virtual hosts.

## Certificate

```bash
sudo certbot certificates
sudo certbot renew --dry-run
```

Current certificate renewal is handled by the standard Certbot systemd timer. The API process never reads certificate private keys.

## Verification

```bash
curl -fsS https://147.15.103.217.sslip.io/md2html/health
curl -fsSI https://147.15.103.217.sslip.io/md2html/
```

Expected: health `status=ok`, TLS certificate hostname match, `HEAD` status 200, and `X-Forwarded-Proto: https` at the proxy boundary.
