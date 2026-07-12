#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.env"
  set +a
fi

export CLIPROXY_LOCAL_TOKEN="${CLIPROXY_LOCAL_TOKEN:-${LITELLM_MASTER_KEY:-}}"
: "${CLIPROXY_LOCAL_TOKEN:?Set CLIPROXY_LOCAL_TOKEN (or legacy LITELLM_MASTER_KEY)}"

base_url="http://127.0.0.1:${CLIPROXY_PORT:-8317}"
if curl --fail --silent \
  -H "Authorization: Bearer $CLIPROXY_LOCAL_TOKEN" \
  "$base_url/v1/models" >/dev/null 2>&1; then
  exit 0
fi

mkdir -p "$SCRIPT_DIR/.runtime"
proxy_pid=""
if [[ "$(uname -s)" == "Darwin" ]]; then
  proxy_command="$(command -v cliproxyapi || command -v cli-proxy-api || true)"
  [[ -n "$proxy_command" ]] || { echo "CLIProxyAPI is not installed" >&2; exit 127; }
  launch_runtime="$HOME/Library/Application Support/AzureClaudexProxy"
  python3 "$SCRIPT_DIR/scripts/render_config.py" \
    "$SCRIPT_DIR/config.cliproxy.template.yaml" \
    "$launch_runtime/config.yaml"
  launchctl remove com.wildcat.azure-claudex-proxy >/dev/null 2>&1 || true
  launchctl remove com.openai-codex-claude-code-proxy >/dev/null 2>&1 || true
  launchctl submit -l com.openai-codex-claude-code-proxy -- \
    "$proxy_command" -config "$launch_runtime/config.yaml"
else
  nohup "$SCRIPT_DIR/start-cliproxy.sh" \
    >"$SCRIPT_DIR/.runtime/proxy.log" 2>&1 &
  proxy_pid=$!
  echo "$proxy_pid" >"$SCRIPT_DIR/.runtime/proxy.pid"
fi

for _ in {1..80}; do
  if [[ -n "$proxy_pid" ]] && ! kill -0 "$proxy_pid" 2>/dev/null; then
    echo "CLIProxyAPI exited during startup; see .runtime/proxy.log" >&2
    exit 1
  fi
  if curl --fail --silent \
    -H "Authorization: Bearer $CLIPROXY_LOCAL_TOKEN" \
    "$base_url/v1/models" >/dev/null 2>&1; then
    exit 0
  fi
  sleep 0.25
done

echo "CLIProxyAPI did not become ready; see .runtime/proxy.log" >&2
exit 1
