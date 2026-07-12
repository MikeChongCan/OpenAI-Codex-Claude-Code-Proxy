#!/usr/bin/env python3
"""Render CLIProxyAPI config without committing credentials."""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys


REQUIRED = ("AZURE_API_BASE", "AZURE_API_KEY", "CLIPROXY_LOCAL_TOKEN")


def normalized_base_url(value: str) -> str:
    value = value.rstrip("/")
    if not value.endswith("/openai/v1"):
        raise ValueError("AZURE_API_BASE must end in /openai/v1")
    return value


def render(template: str, env: dict[str, str]) -> str:
    missing = [name for name in REQUIRED if not env.get(name)]
    if missing:
        raise ValueError(f"missing required environment variables: {', '.join(missing)}")

    default_deployment = env.get("AZURE_DEFAULT_DEPLOYMENT", "gpt-5.6-sol")
    values: dict[str, str | int] = {
        "AZURE_API_BASE": normalized_base_url(env["AZURE_API_BASE"]),
        "AZURE_API_KEY": env["AZURE_API_KEY"],
        "AZURE_OPUS_DEPLOYMENT": env.get("AZURE_OPUS_DEPLOYMENT", default_deployment),
        "AZURE_SONNET_DEPLOYMENT": env.get("AZURE_SONNET_DEPLOYMENT", default_deployment),
        "AZURE_HAIKU_DEPLOYMENT": env.get("AZURE_HAIKU_DEPLOYMENT", default_deployment),
        "CLIPROXY_LOCAL_TOKEN": env["CLIPROXY_LOCAL_TOKEN"],
        "CLIPROXY_AUTH_DIR": env.get("CLIPROXY_AUTH_DIR", str(Path.home() / ".cli-proxy-api")),
        "CLIPROXY_PORT": int(env.get("CLIPROXY_PORT", "8317")),
    }
    for name, value in values.items():
        replacement = str(value) if isinstance(value, int) else json.dumps(value)
        template = template.replace(f"__{name}__", replacement)
    return template


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: render_config.py TEMPLATE OUTPUT", file=sys.stderr)
        return 2
    template_path, output_path = map(Path, sys.argv[1:])
    try:
        rendered = render(template_path.read_text(), dict(os.environ))
    except (OSError, ValueError) as error:
        print(f"config error: {error}", file=sys.stderr)
        return 1
    output_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    output_path.write_text(rendered)
    output_path.chmod(0o600)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
