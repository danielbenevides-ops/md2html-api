# MD2HTML API — Markdown-to-HTML freemium API in a single Python stdlib process.
# Image: ~50MB, no build deps, no PyPI packages.

FROM python:3.12-slim

LABEL org.opencontainers.image.title="md2html-api" \
      org.opencontainers.image.description="Freemium Markdown-to-HTML API with billing, analytics, and security hardening" \
      org.opencontainers.image.version="1.2.0" \
      org.opencontainers.image.source="https://github.com/pqcai/autonomous-business-product"

# curl is needed for the docker-compose healthcheck (HTTP probe to /health).
# python:3.12-slim ships without it; install in one layer, then clean apt cache
# to keep the image small and avoid the "image can't locate curl" healthcheck failure.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# stdlib-only app — no pip install step. requirements.txt is present but empty.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Application files. Copy each explicitly so the image stays lean and
# unrelated artifacts (deploy.sh, *.json ledgers, blog/, etc.) never enter it.
COPY server.py billing.py analytics.py extra_endpoints.py index.html ./

# Runtime state: wallet.json holds the LTC payment address; ledger.json and
# usage.json are written at runtime by billing.py. Copy wallet.json so the
# container boots with a real address; the ledgers are created on first call.
# These are optional — server.py falls back to a hardcoded address if missing.
COPY wallet.json* ./

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8777

EXPOSE 8777

# ThreadingHTTPServer serves on 0.0.0.0:8777 (hardcoded in server.py).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8777/health || exit 1

CMD ["python", "server.py"]
