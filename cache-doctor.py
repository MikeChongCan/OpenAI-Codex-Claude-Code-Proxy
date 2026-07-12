#!/usr/bin/env python3
"""Prove Azure prompt-cache hits survive the Anthropic protocol bridge."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request


def request_message(base_url: str, token: str, suffix: str) -> dict:
    # The stable system prefix intentionally exceeds Azure's 1,024-token cache
    # threshold. Only content after that prefix changes between requests.
    stable_prefix = "Cache-contract stable prefix. " * 650
    payload = json.dumps(
        {
            "model": "azure-opus",
            "max_tokens": 8,
            "system": stable_prefix,
            "messages": [{"role": "user", "content": f"Reply only OK. Run {suffix}"}],
        }
    ).encode()
    request = urllib.request.Request(
        f"{base_url}/v1/messages",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.load(response)


def main() -> int:
    token = os.environ.get("CLIPROXY_LOCAL_TOKEN") or os.environ.get("LITELLM_MASTER_KEY")
    if not token:
        print("CLIPROXY_LOCAL_TOKEN is required", file=sys.stderr)
        return 2
    base_url = f"http://127.0.0.1:{os.environ.get('CLIPROXY_PORT', '8317')}"
    try:
        first = request_message(base_url, token, "one")
        second = request_message(base_url, token, "two")
    except (urllib.error.URLError, TimeoutError) as error:
        print(f"cache check failed: {error}", file=sys.stderr)
        return 1

    first_cached = int(first.get("usage", {}).get("cache_read_input_tokens", 0))
    second_cached = int(second.get("usage", {}).get("cache_read_input_tokens", 0))
    print(f"first cached tokens: {first_cached}")
    print(f"second cached tokens: {second_cached}")
    if second_cached < 1024:
        print(
            "FAIL no measurable Azure prefix-cache hit through CLIProxyAPI",
            file=sys.stderr,
        )
        return 1
    print("OK Azure prompt caching is preserved through the proxy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
