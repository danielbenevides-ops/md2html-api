#!/usr/bin/env bash
# deploy.sh — Start/stop the Markdown-to-HTML API server.
# Works on Linux (Ubuntu) and Windows (git-bash / MSYS).
# Usage:
#   ./deploy.sh start    — launch server in background
#   ./deploy.sh stop     — kill running server
#   ./deploy.sh status   — check if running
#   ./deploy.sh restart  — stop then start
#
# -----------------------------------------------------------------------------
# Reverse proxy: expose port 8777 on port 80 (run as root on the VPS).
# -----------------------------------------------------------------------------
# NGINX  — /etc/nginx/sites-available/mdapi  then  ln -s ../sites-available/mdapi /etc/nginx/sites-enabled/
#   server {
#       listen 80;
#       server_name _;
#       location / {
#           proxy_pass http://127.0.0.1:8777;
#           proxy_set_header Host $host;
#           proxy_set_header X-Real-IP $remote_addr;
#           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
#       }
#   }
#   # Reload: sudo nginx -t && sudo systemctl reload nginx
#
# CADDY  — /etc/caddy/Caddyfile
#   :80 {
#       reverse_proxy 127.0.0.1:8777
#   }
#   # Reload: sudo systemctl reload caddy
# -----------------------------------------------------------------------------

set -euo pipefail

# --- Paths --------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVER_PY_SRC="$SCRIPT_DIR/server.py"
SERVER_PY="$SERVER_PY_SRC"
# On git-bash/MSYS, 'python' is a native Windows binary that cannot read
# MSYS-style paths like /c/Users/...; convert to a native Windows path.
if command -v cygpath >/dev/null 2>&1; then
    SERVER_PY="$(cygpath -w "$SERVER_PY_SRC")"
fi
PID_FILE="$SCRIPT_DIR/.deploy.pid"
LOG_FILE="$SCRIPT_DIR/.deploy.log"
PORT="${PORT:-8777}"
HEALTH_URL="http://localhost:${PORT}/health"

# --- Python launcher (works in git-bash: 'python' exists, 'python3' may not) --
if command -v python >/dev/null 2>&1; then
    PY=python
elif command -v python3 >/dev/null 2>&1; then
    PY=python3
else
    echo "ERROR: no python found in PATH" >&2
    exit 1
fi

# --- Helpers ------------------------------------------------------------------
is_running() {
    [ -f "$PID_FILE" ] || return 1
    local pid
    pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    [ -n "$pid" ] || return 1
    # kill -0 works on both Linux and MSYS/git-bash
    kill -0 "$pid" 2>/dev/null
}

start() {
    if is_running; then
        echo "Server already running (PID $(cat "$PID_FILE"))."
        return 0
    fi
    [ -f "$SERVER_PY_SRC" ] || { echo "ERROR: $SERVER_PY_SRC not found" >&2; exit 1; }
    echo "Starting server: $PY $SERVER_PY  (port $PORT)"
    cd "$SCRIPT_DIR"
    # If we converted to a Windows path above, also run from the Windows dir.
    # nohup + & -> background
    nohup "$PY" "$SERVER_PY" >"$LOG_FILE" 2>&1 &
    echo $! >"$PID_FILE"
    echo "Started PID $(cat "$PID_FILE"). Log: $LOG_FILE"

    # Health check: poll up to ~15s
    echo -n "Health check $HEALTH_URL ... "
    local ok=0
    for i in $(seq 1 15); do
        if curl -fsS "$HEALTH_URL" >/dev/null 2>&1; then
            ok=1
            break
        fi
        sleep 1
    done
    if [ "$ok" = 1 ]; then
        echo "OK"
        echo "Ready: $HEALTH_URL"
    else
        echo "FAILED (no response after 15s). Check $LOG_FILE"
        return 1
    fi
}

stop() {
    local pid=""
    # 1. Try the recorded PID first.
    if [ -f "$PID_FILE" ]; then
        pid="$(cat "$PID_FILE" 2>/dev/null || true)"
    fi
    # 2. On git-bash the recorded PID is the MSYS wrapper; the real Windows
    #    python.exe listens on the port. Find the PID owning the port and
    #    kill that too. Works on Linux (ss/lsof) and Windows/MSYS (netstat).
    local port_pid=""
    if command -v ss >/dev/null 2>&1; then
        port_pid="$(ss -ltnp 2>/dev/null | grep ":${PORT} " | grep -oP 'pid=\K[0-9]+' | head -1 || true)"
    elif command -v lsof >/dev/null 2>&1; then
        port_pid="$(lsof -ti tcp:"${PORT}" -sTCP:LISTEN 2>/dev/null | head -1 || true)"
    elif command -v netstat >/dev/null 2>&1; then
        # Windows netstat: "...LISTENING  <pid>"
        port_pid="$(netstat -ano 2>/dev/null | grep ":${PORT} .*LISTENING" | awk '{print $NF}' | head -1 || true)"
    fi
    if [ -z "$pid" ] && [ -z "$port_pid" ]; then
        echo "Server not running."
        rm -f "$PID_FILE" 2>/dev/null || true
        return 0
    fi
    if [ -n "$pid" ]; then
        echo "Stopping PID $pid ..."
        kill "$pid" 2>/dev/null || true
        for i in $(seq 1 5); do
            kill -0 "$pid" 2>/dev/null || break
            sleep 1
        done
        kill -9 "$pid" 2>/dev/null || true
    fi
    # Also kill the actual port owner (handles git-bash wrapper-vs-child case).
    if [ -n "$port_pid" ] && [ "$port_pid" != "$pid" ]; then
        echo "Stopping port-owner PID $port_pid ..."
        kill "$port_pid" 2>/dev/null || true
        sleep 1
        # On Windows MSYS, kill -9 may not reach a non-child native process;
        # fall back to taskkill if present.
        if command -v taskkill >/dev/null 2>&1; then
            taskkill //PID "$port_pid" //F >/dev/null 2>&1 || true
            taskkill //PID "$port_pid" //T //F >/dev/null 2>&1 || true
        fi
        kill -9 "$port_pid" 2>/dev/null || true
    fi
    # Final resolve: use powershell Stop-Process on Windows if still alive.
    if command -v powershell >/dev/null 2>&1 && [ -n "$port_pid" ]; then
        powershell -Command "Stop-Process -Id $port_pid -Force -ErrorAction SilentlyContinue" 2>/dev/null || true
    fi
    rm -f "$PID_FILE" 2>/dev/null || true
    echo "Stopped."
}

status() {
    if is_running; then
        echo "Running (PID $(cat "$PID_FILE"))."
        curl -fsS "$HEALTH_URL" 2>/dev/null && echo
    else
        echo "Not running."
        return 1
    fi
}

case "${1:-}" in
    start)   start ;;
    stop)    stop ;;
    restart) stop || true; start ;;
    status)  status ;;
    *) echo "Usage: $0 {start|stop|restart|status}" >&2; exit 1 ;;
esac
