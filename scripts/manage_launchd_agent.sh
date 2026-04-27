#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

LABEL="${HORIZON_LAUNCHD_LABEL:-io.yunque.horizon.daily}"
PLIST_PATH="${HOME}/Library/LaunchAgents/${LABEL}.plist"
DOMAIN="gui/$(id -u)"
HOUR="${HORIZON_SCHEDULE_HOUR:-8}"
MINUTE="${HORIZON_SCHEDULE_MINUTE:-30}"
LOG_DIR="${PROJECT_DIR}/logs"
OUT_LOG="${LOG_DIR}/launchd.stdout.log"
ERR_LOG="${LOG_DIR}/launchd.stderr.log"

mkdir -p "$LOG_DIR" "${HOME}/Library/LaunchAgents"

write_plist() {
  /usr/bin/python3 - <<PY
from pathlib import Path
from plistlib import dump

plist = {
    "Label": "${LABEL}",
    "ProgramArguments": ["/bin/zsh", "-lc", "cd '${PROJECT_DIR}' && ./scripts/daily-run.sh"],
    "WorkingDirectory": "${PROJECT_DIR}",
    "RunAtLoad": False,
    "StartCalendarInterval": [{"Hour": int("${HOUR}"), "Minute": int("${MINUTE}")}],
    "StandardOutPath": "${OUT_LOG}",
    "StandardErrorPath": "${ERR_LOG}",
}

path = Path("${PLIST_PATH}")
with path.open("wb") as handle:
    dump(plist, handle)
print(path)
PY
}

install_agent() {
  write_plist >/dev/null
  launchctl bootout "$DOMAIN" "$PLIST_PATH" >/dev/null 2>&1 || true
  launchctl bootstrap "$DOMAIN" "$PLIST_PATH"
  launchctl enable "${DOMAIN}/${LABEL}" >/dev/null 2>&1 || true
  echo "Installed ${LABEL} at ${PLIST_PATH}"
  echo "Schedule: $(printf '%02d:%02d' "$HOUR" "$MINUTE") local time"
}

uninstall_agent() {
  launchctl bootout "$DOMAIN" "$PLIST_PATH" >/dev/null 2>&1 || true
  rm -f "$PLIST_PATH"
  echo "Removed ${LABEL}"
}

status_agent() {
  if [[ -f "$PLIST_PATH" ]]; then
    echo "plist: ${PLIST_PATH}"
    launchctl print "${DOMAIN}/${LABEL}"
  else
    echo "Agent is not installed"
    exit 1
  fi
}

print_plist() {
  write_plist >/dev/null
  plutil -p "$PLIST_PATH"
}

case "${1:-status}" in
  install)
    install_agent
    ;;
  uninstall)
    uninstall_agent
    ;;
  reinstall)
    uninstall_agent || true
    install_agent
    ;;
  status)
    status_agent
    ;;
  print)
    print_plist
    ;;
  *)
    echo "Usage: $0 {install|uninstall|reinstall|status|print}"
    exit 1
    ;;
esac
