#!/usr/bin/env bash
# QA test script for LinkPeek API public endpoints
# Tests top 15 most useful endpoints with https://github.com as sample input

BASE="http://147.15.103.217.sslip.io"
TEST_URL="https://github.com"
OUT="$HOME/autonomous-business-product/test_results.md"

# Endpoints: name|path|extra-curl-args
# Some need url param, some need text, etc.
ENDPOINTS=(
  "preview|/api/preview?url=|"
  "qr|/api/qr?url=|"
  "health|/api/health|"
  "word-count|/api/word-count?url=|"
  "shortlink|/api/shortlink?url=|"
  "tech-stack|/api/tech-stack?url=|"
  "readability|/api/readability?url=|"
  "screenshot-url-hint|/api/screenshot-url-hint?url=|"
  "ssl-info|/api/ssl-info?url=|"
  "dns-lookup|/api/dns-lookup?url=|"
  "og-image|/api/og-image?url=|"
  "uuid|/api/uuid|"
  "hash-text|/api/hash-text?text=hello|"
  "password-strength|/api/password-strength?password=Test1234!|"
  "cron-parser|/api/cron-parser?expr=0%209%20*%20*%20*|"
)

mkdir -p "$(dirname "$OUT")"

{
  echo "# LinkPeek API QA Test Results"
  echo ""
  echo "**Base URL:** $BASE"
  echo "**Test input URL:** $TEST_URL"
  echo "**Test run:** $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
  echo ""
  echo "| # | Endpoint | Path | HTTP Status | Response Time (s) | Body Size | Valid Body | Result |"
  echo "|---|----------|------|------------|-------------------|-----------|-----------|--------|"

  PASS=0
  FAIL=0
  i=0
  for entry in "${ENDPOINTS[@]}"; do
    i=$((i+1))
    name="${entry%%|*}"
    rest="${entry#*|}"
    path="${rest%%|*}"
    extra="${rest#*|}"

    # Build full path: if path ends with "url=" or "text=" append encoded URL/text
    full_path="$path"
    case "$path" in
      *"url=") full_path="${path}$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote('$TEST_URL', safe=''))")" ;;
      *"text=") ;; # text already inline
    esac

    url="$BASE$full_path"

    # Time the curl request; capture body to temp file
    tmp=$(mktemp)
    start=$(python3 -c "import time; print(time.time())")
    http_code=$(curl -s -o "$tmp" -w "%{http_code}" --max-time 30 "$url" 2>/dev/null)
    end=$(python3 -c "import time; print(time.time())")
    elapsed=$(python3 -c "print(f'{$end - $start:.3f}')")
    body_size=$(wc -c < "$tmp" | tr -d ' ')

    # Determine if body is valid: not empty, not pure error JSON
    valid="YES"
    result="PASS"
    if [ -z "$http_code" ] || [ "$http_code" = "000" ]; then
      valid="NO (no response)"
      result="FAIL"
    elif [ "$body_size" -lt 2 ]; then
      valid="NO (empty body)"
      result="FAIL"
    else
      # Check for error indicators
      body_head=$(head -c 500 "$tmp")
      # Common error patterns
      if echo "$body_head" | grep -qiE '"error"\s*:' && [ "$http_code" -ge 400 ]; then
        valid="NO (error JSON)"
        result="FAIL"
      elif echo "$body_head" | grep -qiE '^(Internal Server Error|Service Unavailable|Bad Gateway|Gateway Time-out)'; then
        valid="NO (error text)"
        result="FAIL"
      elif [ "$http_code" -ge 500 ]; then
        valid="NO (5xx)"
        result="FAIL"
      elif [ "$http_code" -ge 400 ]; then
        valid="NO (4xx: $http_code)"
        result="FAIL"
      fi
    fi

    if [ "$result" = "PASS" ]; then PASS=$((PASS+1)); else FAIL=$((FAIL+1)); fi

    # Truncate path for display if too long
    display_path="$full_path"
    if [ ${#display_path} -gt 60 ]; then
      display_path="${display_path:0:57}..."
    fi

    echo "| $i | $name | \`$display_path\` | $http_code | $elapsed | ${body_size}B | $valid | **$result** |"

    rm -f "$tmp"
  done

  echo ""
  echo "## Summary"
  echo ""
  echo "- **Total endpoints tested:** 15"
  echo "- **Passed:** $PASS"
  echo "- **Failed:** $FAIL"
  echo "- **Pass rate:** $(( PASS * 100 / 15 ))%"
  echo ""
  echo "## Notes"
  echo "- All endpoints hit with sample input \`$TEST_URL\` where a URL parameter is accepted."
  echo "- \`/api/qr\` returns a PNG image binary; validity = non-empty, 2xx response."
  echo "- \`/api/uuid\`, \`/api/hash-text\`, \`/api/password-strength\`, \`/api/cron-parser\` do not take a URL."
  echo "- Response time is wall-clock from curl start to body receipt."
} > "$OUT"

echo "Results written to $OUT"
echo "---"
head -40 "$OUT"
