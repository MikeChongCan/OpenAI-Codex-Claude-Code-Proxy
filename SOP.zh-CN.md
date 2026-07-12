# Azure Claudex Proxy 使用 SOP

## 首次准备

进入项目目录：

```bash
cd /Volumes/SandE/temp/202607/azure-claudex-proxy
```

确认 `.env` 已存在。它需要包含 Azure OpenAI 地址、API Key 和模型部署名称。

安装依赖：

```bash
brew install cliproxyapi
```

## 日常使用

直接启动 Claude Code：

```bash
./claudex
```

`claudex` 会自动在后台启动代理，不需要另开终端运行服务器。
默认模型为 Azure `gpt-5.6-sol`，并强制启用 Claude Code effort 模式。

切换其他 Azure 模型：

```bash
CLAUDEX_MODEL=gpt-5.6-terra ./claudex
CLAUDEX_MODEL=gpt-5.6-luna ./claudex
```

使用已登录 CLIProxyAPI 的 OpenAI Codex 官方账号：

```bash
./claudex-oai
./claudex-oai -p "请只回复：OpenAI 代理正常"
```

默认使用 `gpt-5.4`。切换官方 Codex 模型：

```bash
CLAUDEX_OAI_MODEL=gpt-5.5 ./claudex-oai
```

单次执行 Prompt：

```bash
./claudex -p "请只回复：代理运行正常"
```

## 检查代理

检查 Azure、代理和协议转换是否正常：

```bash
./doctor.sh
```

正常输出：

```text
OK CLIProxyAPI, Azure OpenAI, and Anthropic translation are working
```

## 检查 Azure 缓存

此测试会产生两次小额 Azure API 请求：

```bash
set -a
source .env
set +a
./cache-doctor.py
```

正常输出应包含：

```text
OK Azure prompt caching is preserved through the proxy
```

## 停止代理

```bash
./stop-cliproxy.sh
```

下次运行 `./claudex` 时，代理会自动重新启动。

## 手动调试

如果自动启动失败，先停止后台代理，再以前台模式运行：

```bash
./stop-cliproxy.sh
./start-cliproxy.sh
```

然后在另一个终端运行：

```bash
./doctor.sh
```

## 常见提示

- 出现 `claude.ai connectors are disabled` 属于当前代理认证模式的正常提示。
- 不要提交 `.env`、Azure API Key 或 `.runtime` 目录。
- 代理只监听 `127.0.0.1`，不要改成公网地址。
