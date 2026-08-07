#!/usr/bin/env bash
# Hardening verification tests for server.py
set +e
B=http://localhost:8777
python -c "import sys; sys.stdout.write('x'*1100000)" > /tmp/big2.txt
# also keep it pipable for the 413 test (curl --data-binary @file breaks on MSYS paths)
big2=/tmp/big2.txt
PASS=0; FAIL=0
check() {
  local name="$1" want="$2" got="$3"
  if [ "$got" = "$want" ]; then echo "PASS  $name -> [$got]"; PASS=$((PASS+1))
  else echo "FAIL  $name -> got [$got], want [$want]"; FAIL=$((FAIL+1)); fi
}
echo "=== ENDPOINT + EDGE CASE TEST MATRIX ==="
code=$(curl -s -o /dev/null -w "%{http_code}" $B/health);            check "GET /health (v+uptime)"        200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" $B/docs);             check "GET /docs"                      200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" $B/payment);          check "GET /payment"                  200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" $B/usage);            check "GET /usage"                    200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" $B/stats);            check "GET /stats"                    200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" $B/unknown);          check "GET /unknown"                  404 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" -X OPTIONS $B/convert); check "OPTIONS /convert (preflight)" 204 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $B/convert -H "Content-Type: application/json" -d '{"markdown":"# hi"}'); check "POST /convert normal" 200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $B/convert -H "Content-Type: text/plain" --data "");                   check "POST /convert empty body" 400 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $B/convert -H "Content-Type: application/json" -d '{"markdown":""}');     check "POST /convert empty md field" 200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $B/convert -H "Content-Type: application/json" -d '{"markdown":"   "}')  ; check "POST /convert whitespace md" 200 "$code"
code=$(curl -s -o /dev/null -w "%{http_code}" -X POST $B/convert -H "Content-Type: text/plain" --data-binary @/tmp/big2.txt); check "POST /convert >1MB (413)" 413 "$code"
# CORS header presence on a GET and a POST
acao=$(curl -s -D - -o /dev/null $B/health | grep -i "^access-control-allow-origin" | tr -d '\r' | awk '{print $2}')
check "CORS ACAO=* on GET /health"  "*" "$acao"
acao=$(curl -s -D - -o /dev/null -X POST $B/convert -H "Content-Type: application/json" -d '{"markdown":"x"}' | grep -i "^access-control-allow-origin" | tr -d '\r' | awk '{print $2}')
check "CORS ACAO=* on POST /convert" "*" "$acao"
echo ""
echo "RESULTS: $PASS passed, $FAIL failed"
exit $FAIL
