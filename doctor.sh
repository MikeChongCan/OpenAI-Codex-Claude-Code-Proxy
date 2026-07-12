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

if ! command -v cliproxyapi >/dev/null && ! command -v cli-proxy-api >/dev/null; then
  echo "FAIL CLIProxyAPI is not installed"
  exit 1
fi
command -v claude >/dev/null || { echo "FAIL claude is not installed"; exit 1; }

ready=false
for _ in {1..20}; do
  if curl --fail --silent \
    -H "Authorization: Bearer $CLIPROXY_LOCAL_TOKEN" \
    "$base_url/v1/models" >/dev/null; then
    ready=true
    break
  fi
  sleep 0.25
done
if [[ "$ready" != true ]]; then
  echo "FAIL proxy did not become ready at $base_url" >&2
  exit 1
fi

response="$(curl --fail --silent --show-error \
  -H "Authorization: Bearer $CLIPROXY_LOCAL_TOKEN" \
  -H 'anthropic-version: 2023-06-01' \
  -H 'content-type: application/json' \
  "$base_url/v1/messages" \
  -d '{"model":"azure-haiku","max_tokens":16,"messages":[{"role":"user","content":"Reply with exactly: proxy-ok"}]}')"

python3 -c 'import json,sys; data=json.load(sys.stdin); assert data.get("type") == "message"; assert data.get("content")' <<<"$response"
echo "OK CLIProxyAPI, Azure OpenAI, and Anthropic translation are working"
