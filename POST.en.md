# Post

You can run Claude Code on GPT-5.6 Sol in a few steps:

1. Install CLIProxyAPI.
2. Connect Azure OpenAI or sign in with your OpenAI/Codex subscription.
3. Point `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` at the local proxy.
4. Create a `claudex` launcher with GPT-5.6 Sol, effort mode, and automatic proxy startup.

That’s it—you keep Claude Code and choose which GPT provider pays for the run. Credit to Theo for sharing the idea.

Paste this into your coding agent:

`Set up CLIProxyAPI as a localhost-only gateway for Claude Code using GPT-5.6 Sol, support either Azure OpenAI API credentials or OpenAI Codex OAuth, create a safe claudex launcher that auto-starts the proxy and enables effort mode, preserve prompt caching, keep secrets out of Git, and run a real claude -p tool-use smoke test.`
