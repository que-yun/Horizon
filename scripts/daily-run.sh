#!/usr/bin/env bash
# Horizon local daily run:
# 1. update repo on main
# 2. ensure local services are running
# 3. generate the summary locally
# 4. commit/push docs changes to main
# 5. let GitHub Actions deploy Pages
# 6. send a Feishu/Lark bot notification

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_BIN="$PROJECT_DIR/.venv/bin"
EXTERNAL_RUN_DATE="${HORIZON_RUN_DATE:-}"
EXTERNAL_RUN_HOURS="${HORIZON_RUN_HOURS:-}"
EXTERNAL_REMOTE_NAME="${HORIZON_GIT_REMOTE:-}"
EXTERNAL_BRANCH_NAME="${HORIZON_GIT_BRANCH:-}"
EXTERNAL_UV_BIN="${HORIZON_UV_BIN:-}"
EXTERNAL_PAGES_URL="${HORIZON_PAGES_URL:-}"

cd "$PROJECT_DIR"

log() {
  printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

resolve_uv() {
  if command -v uv >/dev/null 2>&1; then
    command -v uv
    return 0
  fi
  if [[ -x "$HOME/.local/bin/uv" ]]; then
    printf '%s\n' "$HOME/.local/bin/uv"
    return 0
  fi
  if [[ -x "/opt/homebrew/bin/uv" ]]; then
    printf '%s\n' "/opt/homebrew/bin/uv"
    return 0
  fi
  return 1
}

sync_dependencies() {
  local uv_bin="$1"
  if [[ -n "$uv_bin" ]]; then
    "$uv_bin" sync --quiet
    return 0
  fi
  "$VENV_BIN/pip" install -e . >/dev/null
}

run_horizon() {
  local uv_bin="$1"
  if [[ -n "$uv_bin" ]]; then
    HORIZON_RUN_DATE="$RUN_DATE" "$uv_bin" run horizon --hours "$RUN_HOURS"
    return 0
  fi
  HORIZON_RUN_DATE="$RUN_DATE" "$VENV_BIN/horizon" --hours "$RUN_HOURS"
}

ensure_rsshub() {
  local container_name="horizon-rsshub"
  local status
  status="$(docker inspect -f '{{.State.Status}}' "$container_name" 2>/dev/null || true)"

  if [[ "$status" == "running" ]]; then
    return 0
  fi
  if [[ -n "$status" ]]; then
    docker start "$container_name" >/dev/null
    return 0
  fi

  docker compose -f docker-compose.local.yml up -d rsshub >/dev/null
}

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

# Local automation already uses FEISHU_BOT_WEBHOOK_URL for status cards.
# Reuse the same bot for summary webhook delivery unless a dedicated
# HORIZON_WEBHOOK_URL is explicitly configured.
if [[ -z "${HORIZON_WEBHOOK_URL:-}" && -n "${FEISHU_BOT_WEBHOOK_URL:-}" ]]; then
  export HORIZON_WEBHOOK_URL="$FEISHU_BOT_WEBHOOK_URL"
fi

if [[ -n "$EXTERNAL_PAGES_URL" ]]; then
  export HORIZON_PAGES_URL="$EXTERNAL_PAGES_URL"
fi

RUN_DATE="${EXTERNAL_RUN_DATE:-${HORIZON_RUN_DATE:-$(date '+%Y-%m-%d')}}"
RUN_HOURS="${EXTERNAL_RUN_HOURS:-${HORIZON_RUN_HOURS:-24}}"
REMOTE_NAME="${EXTERNAL_REMOTE_NAME:-${HORIZON_GIT_REMOTE:-origin}}"
BRANCH_NAME="${EXTERNAL_BRANCH_NAME:-${HORIZON_GIT_BRANCH:-main}}"
SUMMARY_PATH="$PROJECT_DIR/data/summaries/horizon-${RUN_DATE}-zh.md"
POST_PATH="$PROJECT_DIR/docs/_posts/${RUN_DATE}-summary-zh.md"
LOCK_DIR="$PROJECT_DIR/.runtime/daily-run.lock"
UV_BIN="${EXTERNAL_UV_BIN:-${HORIZON_UV_BIN:-}}"
STATUS="failed"
FAILED_STEP="init"
DETAIL_MESSAGE=""

if [[ -z "$UV_BIN" ]]; then
  UV_BIN="$(resolve_uv || true)"
fi

derive_pages_url() {
  if [[ -n "${HORIZON_PAGES_URL:-}" ]]; then
    printf '%s' "$HORIZON_PAGES_URL"
    return 0
  fi

  local remote_url
  remote_url="$(git remote get-url "$REMOTE_NAME" 2>/dev/null || true)"
  if [[ -z "$remote_url" ]]; then
    return 0
  fi

  REMOTE_URL="$remote_url" python3 - <<'PY'
import os
import re

remote_url = os.environ.get("REMOTE_URL", "").strip()
match = re.search(r"[:/]([^/]+)/([^/]+?)(?:\.git)?$", remote_url)
if match:
    owner, repo = match.group(1), match.group(2)
    print(f"https://{owner}.github.io/{repo}/", end="")
PY
}

notify_feishu() {
  local status="$1"
  local message="$2"
  local pages_url

  pages_url="$(derive_pages_url)"

  "$PROJECT_DIR/.venv/bin/python" "$PROJECT_DIR/scripts/notify_feishu.py" \
    --status "$status" \
    --date "$RUN_DATE" \
    --summary-path "$SUMMARY_PATH" \
    --pages-url "$pages_url" \
    --source-path "$POST_PATH" \
    --message "$message" || true
}

cleanup() {
  local exit_code="$1"
  rm -rf "$LOCK_DIR"

  if [[ "$exit_code" -ne 0 ]]; then
    notify_feishu "failed" "${FAILED_STEP}: ${DETAIL_MESSAGE:-run failed}"
  elif [[ "$STATUS" == "success" ]]; then
    notify_feishu "success" "${DETAIL_MESSAGE:-本地定时任务执行成功}"
  fi
}

trap 'cleanup $?' EXIT

if [[ -d "$LOCK_DIR" ]]; then
  log "Another daily run is already in progress."
  exit 1
fi
mkdir -p "$LOCK_DIR"

log "Starting Horizon local daily run..."

FAILED_STEP="git-status"
if [[ -n "$(git status --porcelain)" ]]; then
  DETAIL_MESSAGE="git worktree is dirty, automation run aborted to avoid mixing local edits"
  log "$DETAIL_MESSAGE"
  exit 1
fi

FAILED_STEP="git-branch"
CURRENT_BRANCH="$(git branch --show-current)"
if [[ "$CURRENT_BRANCH" != "$BRANCH_NAME" ]]; then
  DETAIL_MESSAGE="current branch is ${CURRENT_BRANCH}, expected ${BRANCH_NAME}; run automation from a dedicated clean clone/worktree on ${BRANCH_NAME}"
  log "$DETAIL_MESSAGE"
  exit 1
fi

FAILED_STEP="env"
AI_KEY_ENV="$(python3 - <<'PY'
import json
from pathlib import Path

config = json.loads(Path("data/config.json").read_text(encoding="utf-8"))
print(config["ai"]["api_key_env"])
PY
)"
if [[ -z "${AI_KEY_ENV}" || -z "${!AI_KEY_ENV:-}" ]]; then
  DETAIL_MESSAGE="required AI credential ${AI_KEY_ENV:-<unknown>} is missing; launchd only reads values from .env or the script environment"
  log "$DETAIL_MESSAGE"
  exit 1
fi

FAILED_STEP="git-pull"
log "Syncing latest code from ${REMOTE_NAME}/${BRANCH_NAME}..."
git fetch --quiet "$REMOTE_NAME" "$BRANCH_NAME"
git pull --ff-only --quiet "$REMOTE_NAME" "$BRANCH_NAME"

FAILED_STEP="deps"
log "Installing/updating dependencies..."
sync_dependencies "$UV_BIN"

FAILED_STEP="rsshub"
log "Ensuring local RSSHub is running..."
ensure_rsshub

FAILED_STEP="changedetection"
log "Ensuring local changedetection.io is running..."
./scripts/run_changedetection.sh start >/dev/null
./.venv/bin/python scripts/sync_changedetection_sources.py --recheck >/dev/null

FAILED_STEP="summary"
log "Running Horizon summary generation..."
run_horizon "$UV_BIN"

FAILED_STEP="verify-output"
if [[ ! -f "$POST_PATH" ]]; then
  DETAIL_MESSAGE="summary post not found at $POST_PATH"
  log "$DETAIL_MESSAGE"
  exit 1
fi

FAILED_STEP="git-commit"
log "Committing docs changes to ${BRANCH_NAME}..."
git add -f "$POST_PATH"

if git diff --cached --quiet; then
  DETAIL_MESSAGE="日报已生成，但 docs 无新变更，跳过提交与推送"
  log "$DETAIL_MESSAGE"
  STATUS="success"
  exit 0
fi

git commit -m "docs: daily summary ${RUN_DATE}"

FAILED_STEP="git-push"
log "Pushing docs changes to ${REMOTE_NAME}/${BRANCH_NAME}..."
git push "$REMOTE_NAME" "HEAD:${BRANCH_NAME}"

STATUS="success"
DETAIL_MESSAGE="日报已生成并推送到 ${REMOTE_NAME}/${BRANCH_NAME}，GitHub Actions 将继续发布 Pages"
log "$DETAIL_MESSAGE"
