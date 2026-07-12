# Azure OpenAI for Claude Code

This repo exposes Azure OpenAI deployments to Claude Code through an
Anthropic-compatible local endpoint. The preferred backend is
[CLIProxyAPI](https://github.com/router-for-me/CLIProxyAPI); the original
LiteLLM configuration remains as a fallback.

## Why CLIProxyAPI

Claude Code speaks Anthropic Messages, including Anthropic SSE streaming and
tool-use blocks. Azure OpenAI speaks the OpenAI protocol. CLIProxyAPI owns that
translation and is actively tested against Claude Code. This wrapper keeps the
Azure credentials out of committed YAML, binds only to localhost, and gives
Claude Code a separate random local credential.

## Setup

Requirements: macOS, Homebrew, Claude Code, Python 3, and an Azure deployment
that supports Chat Completions, streaming, and tool calls.

```bash
brew install cliproxyapi
cp .env.example .env
openssl rand -hex 32
```

Put the generated value in `CLIPROXY_LOCAL_TOKEN`, then set `AZURE_API_BASE`,
`AZURE_API_KEY`, and the Azure deployment names in `.env`. The base URL must be
the GA endpoint ending in `/openai/v1`.

Normally, just run Claude Code. `claudex` starts the proxy as a macOS user
`launchd` job and waits for readiness (non-macOS uses a PID/log fallback):

```bash
./claudex
./claudex -p 'Reply with the active model name only'
```

Lifecycle commands:

```bash
./ensure-cliproxy.sh
./stop-cliproxy.sh
./start-cliproxy.sh  # foreground/debug mode
```

Verify the full Azure round trip in another:

```bash
./doctor.sh
```

Prove prompt caching is preserved (two small billable requests):

```bash
set -a; source .env; set +a
./cache-doctor.py
```

The test sends two requests with an identical prefix longer than 1,024 tokens
through the Anthropic endpoint and requires the second response to report at
least 1,024 `cache_read_input_tokens`. This catches translator changes that
drop cached-token accounting or destabilize the prefix.

For a global `claudex` command, symlink it somewhere already on `PATH`:

```bash
ln -s "$PWD/claudex" "$HOME/.local/bin/claudex"
```

The launcher deliberately unsets `ANTHROPIC_API_KEY` so an existing Anthropic
key cannot accidentally bypass or conflict with the local gateway. It does not
enable `--dangerously-skip-permissions`; pass that explicitly when intended.

## Claude and Codex subscription auth (optional)

CLIProxyAPI can also pool official CLI subscriptions. These are independent of
the Azure provider:

```bash
cliproxyapi -config .runtime/config.yaml -claude-login
cliproxyapi -config .runtime/config.yaml -codex-login
```

Run `./start-cliproxy.sh` once first so the secret-bearing runtime config exists.
OAuth files live in `~/.cli-proxy-api` by default and must never be committed.

## Model mapping

Claude Code's Opus, Sonnet, and Haiku tiers map to `azure-opus`,
`azure-sonnet`, and `azure-haiku`. Set the three `AZURE_*_DEPLOYMENT` variables
when Azure has distinct deployments. Otherwise all tiers use
`AZURE_DEFAULT_DEPLOYMENT`.

Azure is configured as a CLIProxyAPI Codex API-key provider, which uses the
Responses API. This is intentional: GPT-5.6 rejects Chat Completions requests
that combine tools with reasoning, while Claude Code needs both. The Azure
`api-key` header is added alongside CLIProxyAPI's standard bearer header.

## Prompt-cache contract

Azure caching is automatic for GPT-4o and newer models. Cache hits require an
identical prefix of at least 1,024 tokens and are reported by Azure as
`prompt_tokens_details.cached_tokens`; CLIProxyAPI maps that value back to
Anthropic's `usage.cache_read_input_tokens`. For models newer than GPT-5.4,
Azure currently defaults to 24-hour retention.

To keep GPT-5.6 cache hits intact:

- `claudex` does not append a dynamic system prompt.
- The proxy does not inject timestamps, request IDs, or random content into the
  system/message/tool prefix.
- Model aliases are stable across sessions.
- Do not reorder tool definitions or mutate the shared system prompt per turn.
- Run `cache-doctor.py` after CLIProxyAPI upgrades; cached-token accounting is
  part of the release gate.

## Security and operations

- The listener is fixed to `127.0.0.1`; do not expose it to a LAN or the public
  internet without TLS, network controls, and a real secret manager.
- `.runtime/config.yaml` contains the Azure key, is mode `0600`, and is ignored.
- The local proxy token and Azure key must be different.
- `doctor.sh` sends a small billable Azure request.
- `cache-doctor.py` sends two billable Azure requests with a long repeated
  prefix; run it deliberately, not in the offline unit-test suite.
- OAuth subscription use may be governed by provider terms; Azure API-key use
  does not depend on subscription OAuth.

## Legacy LiteLLM fallback

The old path remains available:

```bash
./start-proxy.sh
./start-claude.sh
```

Prefer CLIProxyAPI for Claude Code because its scope is the CLI protocol bridge,
while LiteLLM is a broader gateway with more parameter-normalization behavior.

## Validation

```bash
python3 -m unittest discover -s tests -v
bash -n ensure-cliproxy.sh stop-cliproxy.sh start-cliproxy.sh claudex doctor.sh start-proxy.sh start-claude.sh claude-proxy.sh
```
