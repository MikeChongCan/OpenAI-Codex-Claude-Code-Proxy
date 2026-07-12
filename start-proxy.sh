#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$SCRIPT_DIR/.env" ]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

: "${AZURE_API_BASE:?Set AZURE_API_BASE in .env or environment}"
: "${AZURE_API_KEY:?Set AZURE_API_KEY in .env or environment}"
: "${LITELLM_MASTER_KEY:?Set LITELLM_MASTER_KEY in .env or environment}"

exec uv run litellm --host "${LITELLM_HOST:-127.0.0.1}" --config "$SCRIPT_DIR/config.yaml" "$@"
