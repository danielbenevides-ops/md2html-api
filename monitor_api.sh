#!/bin/bash
# Monitor MD2HTML API - checks health and reports
API="https://147.15.103.217.sslip.io/md2html/health"
RESULT=$(curl -s --max-time 8 "$API" 2>/dev/null)
if [ -z "$RESULT" ]; then
  echo "ALERT: API DOWN at $(date)"
  exit 1
else
  STATUS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)
  echo "OK: API status=$STATUS at $(date)"
  echo "$RESULT"
fi
