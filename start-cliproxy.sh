#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "$SCRIPT_DIR/.env"
  set +a
fi

: "${AZURE_API_BASE:?Set AZURE_API_BASE in .env or the environment}"
: "${AZURE_API_KEY:?Set AZURE_API_KEY in .env or the environment}"
export CLIPROXY_LOCAL_TOKEN="${CLIPROXY_LOCAL_TOKEN:-${LITELLM_MASTER_KEY:-}}"
: "${CLIPROXY_LOCAL_TOKEN:?Set CLIPROXY_LOCAL_TOKEN (or legacy LITELLM_MASTER_KEY)}"

proxy_command=""
for candidate in cliproxyapi cli-proxy-api; do
  if [[ -z "$proxy_command" ]] && command -v "$candidate" >/dev/null 2>&1; then
    proxy_command="$candidate"
    break
  fi
done
if [[ -z "$proxy_command" ]]; then
  echo "CLIProxyAPI is missing. Install it with: brew install cliproxyapi" >&2
  exit 127
fi

runtime_config="$SCRIPT_DIR/.runtime/config.yaml"
python3 "$SCRIPT_DIR/scripts/render_config.py" \
  "$SCRIPT_DIR/config.cliproxy.template.yaml" \
  "$runtime_config"

exec "$proxy_command" -config "$runtime_config" "$@"
