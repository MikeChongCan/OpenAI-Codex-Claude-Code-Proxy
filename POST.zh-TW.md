# 貼文

剛把 Claude Code 接上 GPT-5.6 Sol，底層用 CLIProxyAPI。

我做了兩個簡單的啟動腳本：

- `./claudex` → Azure OpenAI
- `./claudex-oai` → OpenAI／Codex 訂閱

兩邊都會開啟 effort mode、自動啟動 proxy，也能正常使用 Claude Code tools。Azure 的 prompt cache 也有成功命中。

可以繼續用熟悉的橘色螃蟹，同時自由選擇模型從哪裡來。靈感來自 Theo 的分享。
