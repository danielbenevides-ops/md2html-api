#!/bin/bash
# Watch LTC wallet for incoming payments - loops every 60s
WALLET="Lb5EQbYXkzfgnfHcNvqesFQd7ujMtTmMCG"
LOG="payments_log.txt"
echo "Watching $WALLET for payments... (Ctrl+C to stop)" >> "$LOG"
while true; do
  BAL=$(curl -s --max-time 10 "https://api.blockcypher.com/v1/ltc/main/addrs/$WALLET/balance" 2>/dev/null)
  BAL_LTC=$(echo "$BAL" | python3 -c "import sys,json; print(json.load(sys.stdin).get('total_received',0)/100000000)" 2>/dev/null)
  if [ -n "$BAL_LTC" ] && [ "${BAL_LTC%.*}" -gt 0 ] 2>/dev/null; then
    echo "PAYMENT DETECTED: $BAL_LTC LTC at $(date)" >> "$LOG"
    echo "PAYMENT DETECTED: $BAL_LTC LTC at $(date)"
    # Trigger notification
    curl -s --max-time 5 "https://147.15.103.217.sslip.io/md2html/health" >/dev/null 2>&1
  fi
  sleep 60
done
