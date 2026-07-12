# 貼文

幾個步驟就能讓 Claude Code 使用 GPT-5.6 Sol：

1. 安裝 CLIProxyAPI。
2. 連接 Azure OpenAI，或登入 OpenAI／Codex 訂閱。
3. 將 `ANTHROPIC_BASE_URL` 和 `ANTHROPIC_AUTH_TOKEN` 指向本機 proxy。
4. 建立 `claudex` 啟動腳本，指定 GPT-5.6 Sol、開啟 effort mode，並自動啟動 proxy。

完成。保留熟悉的 Claude Code，同時自由選擇由哪個 GPT provider 執行與計費。感謝 Theo 分享這個做法。

把下面這句貼給你的 coding agent：

`請將 CLIProxyAPI 設定為僅監聽 localhost 的 Claude Code gateway，使用 GPT-5.6 Sol，支援 Azure OpenAI API 憑證或 OpenAI Codex OAuth；建立可自動啟動 proxy、開啟 effort mode 的安全 claudex 啟動腳本，保留 prompt cache、不要把 secrets 提交到 Git，最後用真實的 claude -p 工具呼叫完成 smoke test。`
