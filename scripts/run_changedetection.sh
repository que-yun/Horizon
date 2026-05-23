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
READY_TIMEOUT="${CHANGEDETECTION_READY_TIMEOUT:-45}"
CHANGEDETECTION_VENV="${CHANGEDETECTION_VENV:-.runtime/changedetection-venv}"
CHANGEDETECTION_BIN="$PROJECT_DIR/$CHANGEDETECTION_VENV/bin/changedetection.py"

ensure_installed() {
  if [[ -x "$CHANGEDETECTION_BIN" ]]; then
    return 0
  fi

  echo "Installing changedetection.io into $CHANGEDETECTION_VENV ..."
  mkdir -p "$(dirname "$CHANGEDETECTION_VENV")"

  if command -v uv >/dev/null 2>&1; then
    uv venv --python "$PROJECT_DIR/.venv/bin/python" "$CHANGEDETECTION_VENV"
    uv pip install --python "$PROJECT_DIR/$CHANGEDETECTION_VENV/bin/python" --prerelease allow "changedetection.io==0.54.10"
    return 0
  fi

  if [[ -x "$HOME/.local/bin/uv" ]]; then
    "$HOME/.local/bin/uv" venv --python "$PROJECT_DIR/.venv/bin/python" "$CHANGEDETECTION_VENV"
    "$HOME/.local/bin/uv" pip install --python "$PROJECT_DIR/$CHANGEDETECTION_VENV/bin/python" --prerelease allow "changedetection.io==0.54.10"
    return 0
  fi

  "$PROJECT_DIR/.venv/bin/python" -m venv "$CHANGEDETECTION_VENV"
  "$PROJECT_DIR/$CHANGEDETECTION_VENV/bin/python" -m pip install --upgrade pip >/dev/null
  "$PROJECT_DIR/$CHANGEDETECTION_VENV/bin/python" -m pip install --pre "changedetection.io==0.54.10"
}

is_running() {
  if [[ ! -f "$PID_FILE" ]]; then
    return 1
  fi

  local pid
  pid="$(cat "$PID_FILE")"

  if [[ -z "$pid" || ! "$pid" =~ ^[0-9]+$ ]]; then
    rm -f "$PID_FILE"
    return 1
  fi

  if ! kill -0 "$pid" >/dev/null 2>&1; then
    rm -f "$PID_FILE"
    return 1
  fi

  local command
  command="$(ps -p "$pid" -o command= 2>/dev/null || true)"
  if [[ "$command" != *"$CHANGEDETECTION_BIN"* ]]; then
    rm -f "$PID_FILE"
    return 1
  fi

  return 0
}

wait_until_ready() {
  local url="http://$HOST:$PORT/"
  local deadline=$((SECONDS + READY_TIMEOUT))

  while (( SECONDS < deadline )); do
    if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done

  echo "changedetection.io did not become ready on $url within ${READY_TIMEOUT}s"
  echo "Last log lines:"
  tail -n 80 "$LOG_FILE" || true
  return 1
}

start_service() {
  ensure_installed
  mkdir -p "$DATASTORE" "$(dirname "$LOG_FILE")"

  if is_running; then
    echo "changedetection.io is already running on http://$HOST:$PORT"
    wait_until_ready
    return 0
  fi

  nohup "$CHANGEDETECTION_BIN" \
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

  wait_until_ready

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
    wait_until_ready
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
