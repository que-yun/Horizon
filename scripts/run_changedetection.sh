#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

ACTION="${1:-start}"
HOST="${CHANGEDETECTION_HOST:-127.0.0.1}"
PORT="${CHANGEDETECTION_PORT:-15000}"
LOG_LEVEL="${CHANGEDETECTION_LOG_LEVEL:-INFO}"
DATASTORE="${CHANGEDETECTION_DATASTORE:-data/changedetection}"
PID_FILE="$DATASTORE/changedetection.pid"
LOG_FILE="${CHANGEDETECTION_LOG_FILE:-logs/changedetection.log}"

ensure_installed() {
  if [[ -x "$PROJECT_DIR/.venv/bin/changedetection.py" ]]; then
    return 0
  fi

  echo "Installing changedetection.io into .venv ..."
  "$PROJECT_DIR/.venv/bin/pip" install "changedetection.io==0.54.10"
}

is_running() {
  if [[ ! -f "$PID_FILE" ]]; then
    return 1
  fi

  local pid
  pid="$(cat "$PID_FILE")"

  if [[ -z "$pid" ]]; then
    return 1
  fi

  kill -0 "$pid" >/dev/null 2>&1
}

start_service() {
  ensure_installed
  mkdir -p "$DATASTORE" "$(dirname "$LOG_FILE")"

  if is_running; then
    echo "changedetection.io is already running on http://$HOST:$PORT"
    return 0
  fi

  nohup "$PROJECT_DIR/.venv/bin/changedetection.py" \
    -d "$DATASTORE" \
    -C \
    -h "$HOST" \
    -p "$PORT" \
    -l "$LOG_LEVEL" \
    >"$LOG_FILE" 2>&1 &

  local pid=$!
  echo "$pid" >"$PID_FILE"
  sleep 3

  if ! kill -0 "$pid" >/dev/null 2>&1; then
    echo "changedetection.io failed to start. Last log lines:"
    tail -n 40 "$LOG_FILE" || true
    exit 1
  fi

  echo "changedetection.io started on http://$HOST:$PORT"
}

stop_service() {
  if ! is_running; then
    echo "changedetection.io is not running"
    rm -f "$PID_FILE"
    return 0
  fi

  local pid
  pid="$(cat "$PID_FILE")"
  kill "$pid"

  for _ in {1..20}; do
    if ! kill -0 "$pid" >/dev/null 2>&1; then
      rm -f "$PID_FILE"
      echo "changedetection.io stopped"
      return 0
    fi
    sleep 1
  done

  echo "changedetection.io did not stop gracefully, sending SIGKILL"
  kill -9 "$pid" >/dev/null 2>&1 || true
  rm -f "$PID_FILE"
}

status_service() {
  if is_running; then
    echo "changedetection.io is running on http://$HOST:$PORT (pid $(cat "$PID_FILE"))"
  else
    echo "changedetection.io is not running"
    return 1
  fi
}

case "$ACTION" in
  start)
    start_service
    ;;
  stop)
    stop_service
    ;;
  restart)
    stop_service || true
    start_service
    ;;
  status)
    status_service
    ;;
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac
