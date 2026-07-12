#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
pid_file="$SCRIPT_DIR/.runtime/proxy.pid"

if [[ "$(uname -s)" == "Darwin" ]]; then
  if launchctl remove com.wildcat.azure-claudex-proxy >/dev/null 2>&1; then
    echo "CLIProxyAPI stopped"
  else
    echo "CLIProxyAPI is not managed by this repo"
  fi
  rm -f "$pid_file"
  exit 0
fi

if [[ ! -f "$pid_file" ]]; then
  echo "CLIProxyAPI is not managed by this repo"
  exit 0
fi

proxy_pid="$(<"$pid_file")"
if kill -0 "$proxy_pid" 2>/dev/null; then
  kill "$proxy_pid"
  for _ in {1..20}; do
    kill -0 "$proxy_pid" 2>/dev/null || break
    sleep 0.1
  done
fi
rm -f "$pid_file"
echo "CLIProxyAPI stopped"
