FROM python:3.11-slim

LABEL org.opencontainers.image.title="md2html-api" \
      org.opencontainers.image.description="Freemium Markdown-to-HTML API" \
      org.opencontainers.image.source="https://github.com/pqcai/autonomous-business-product"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8777

WORKDIR /app

# The API uses the Python standard library; keep the requirements layer cacheable.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py billing.py analytics.py extra_endpoints.py index.html ./
COPY wallet.json* ./

# Keep mutable state in the mounted /app/data volume. Symlinks preserve the
# app's existing usage.json path and provide a place for api_keys.json.
RUN mkdir -p /app/data \
    && printf '{}\n' > /app/data/usage.json \
    && printf '{}\n' > /app/data/api_keys.json \
    && ln -s /app/data/usage.json /app/usage.json \
    && ln -s /app/data/api_keys.json /app/api_keys.json

EXPOSE 8777

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8777/health', timeout=3)"

CMD ["python", "server.py"]
