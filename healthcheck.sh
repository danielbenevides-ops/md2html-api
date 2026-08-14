#!/usr/bin/env bash
# healthcheck.sh — silent cron health monitor for the md2html API on the VPS.
#
#  1. Curls https://147.15.103.217.sslip.io/md2html/health (5s timeout).
#  2. On failure, SSHs into the VPS and restarts the server via deploy.sh.
#  3. Appends a {ts, up, restarted} entry to uptime.json.
#  4. Silent: no alerts, no stdout unless run manually with -v.
#
# Cron (every 5 min):
#   */5 * * * *  /c/Users/pqcai/autonomous-business-product/healthcheck.sh >/dev/null 2>&1
#
# Manual:  ./healthcheck.sh           (quiet)   ./healthcheck.sh -v  (verbose)

set -uo pipefail   # no 'set -e' — a failed health probe is NOT a script error

# --- Config -------------------------------------------------------------------
VPS_HOST="147.15.103.217"                       # SSH alias from ~/.ssh/config
HEALTH_URL="http://${VPS_HOST}/md2html/health"
HEALTH_TIMEOUT=5                                # seconds
SSH_OPTS="-o ConnectTimeout=10 -o BatchMode=yes -o StrictHostKeyChecking=accept-new"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPTIME_LOG="${SCRIPT_DIR}/uptime.json"
REMOTE_PROJECT_DIR="autonomous-business-product"   # relative to ubuntu's $HOME on the VPS

VERBOSE=0
[ "${1:-}" = "-v" ] && VERBOSE=1

# --- Helpers ------------------------------------------------------------------
now_iso() { date -u +"%Y-%m-%dT%H:%M:%S+00:00"; }

log_verbose() { [ "$VERBOSE" = 1 ] && echo "$*" || true; }

# Append a JSON entry to uptime.json (array, capped at last 1000).
# Usage: append_uptime <up:bool> <restarted:bool>
append_uptime() {
    local up="$1" restarted="$2" ts
    ts="$(now_iso)"
    local entry
    entry=$(printf '{"ts":"%s","up":%s,"restarted":%s}' "$ts" "$up" "$restarted")

    # Read existing array (tolerant of empty/missing/corrupt file).
    local data
    if [ -f "$UPTIME_LOG" ] && [ -s "$UPTIME_LOG" ]; then
        data="$(cat "$UPTIME_LOG" 2>/dev/null || true)"
        case "$data" in
            '['*']') : ;;                          # looks like a JSON array
            *) data="[]" ;;                         # reset if malformed
        esac
    else
        data="[]"
    fi

    # Use python if available (git-bash has it) for robust JSON handling;
    # fall back to a simple text append otherwise.
    if command -v python >/dev/null 2>&1; then
        printf '%s' "$data" | python -c '
import json, sys
try:
    arr = json.loads(sys.stdin.read())
    if not isinstance(arr, list):
        arr = []
except Exception:
    arr = []
entry = json.loads(sys.argv[1])
arr.append(entry)
del arr[:-1000]
print(json.dumps(arr, indent=2))
' "$entry" > "${UPTIME_LOG}.tmp" && mv "${UPTIME_LOG}.tmp" "$UPTIME_LOG"
    else
        # Fallback: text append (may produce slightly non-standard JSON,
        # but preserves history and stays cron-safe).
        if [ "$data" = "[]" ]; then
            printf '[\n  %s\n]\n' "$entry" > "$UPTIME_LOG"
        else
            # insert before the closing bracket
            printf '%s,\n  %s\n]\n' "${data%]}" "$entry" > "$UPTIME_LOG"
        fi
    fi
}

# --- Main ---------------------------------------------------------------------
log_verbose "[healthcheck] probing $HEALTH_URL (timeout ${HEALTH_TIMEOUT}s)"

up=0
restarted=0

if curl -fsS --max-time "$HEALTH_TIMEOUT" "$HEALTH_URL" >/dev/null 2>&1; then
    up=1
    log_verbose "[healthcheck] UP"
else
    log_verbose "[healthcheck] DOWN — attempting remote restart via SSH"
    # SSH in and run deploy.sh restart on the VPS.
    if ssh $SSH_OPTS "$VPS_HOST" \
        "cd ~/${REMOTE_PROJECT_DIR} && bash deploy.sh restart" >/dev/null 2>&1; then
        restarted=1
        log_verbose "[healthcheck] restart command sent; re-probing in 8s"
        sleep 8
        if curl -fsS --max-time "$HEALTH_TIMEOUT" "$HEALTH_URL" >/dev/null 2>&1; then
            up=1
            log_verbose "[healthcheck] UP after restart"
        else
            log_verbose "[healthcheck] still DOWN after restart"
        fi
    else
        log_verbose "[healthcheck] SSH/restart FAILED"
    fi
fi

append_uptime "$up" "$restarted"
log_verbose "[healthcheck] logged: up=$up restarted=$restarted -> $UPTIME_LOG"

# Exit 0 always (silent monitoring — cron should never page on this).
exit 0
