# DeepSeek Chat Backup：你的 AI 对话保险箱

> 借鉴 GitHub Top10 项目的设计精华，打造最安全的 DeepSeek 聊天记录备份工具

## 为什么需要这个工具？

你有没有遇到过这些情况：

- DeepSeek 聊天记录太多，想找之前的对话却翻不到
- 担心账号出问题，聊天记录全丢
- 想把有价值的对话导出保存，却没有官方工具
- 想用 AI 训练自己的数据，却不知道怎么提取

**DeepSeek Chat Backup** 就是为解决这些问题而生的。

## 核心特性

### 1. PII 智能脱敏

借鉴 DataClaw 的设计理念，自动识别并脱敏：

| 类型 | 原始 | 脱敏后 |
|------|------|--------|
| 手机号 | 13812345678 | 138****5678 |
| 邮箱 | test@example.com | te***@example.com |
| 身份证 | 110101199001011234 | 110101199****1234 |
| API Key | token=abc123 | token=***REDACTED*** |

```bash
python scripts/backup.py --pii
```

### 2. 全文搜索

借鉴 Kept 项目的 SQLite FTS5 设计，构建本地搜索索引：

```bash
# 构建索引
python scripts/export.py --build-index

# 搜索
python scripts/export.py --search "Lambda架构"
```

### 3. 多格式导出

| 格式 | 用途 |
|------|------|
| Markdown | 阅读、文档 |
| Word | 正式报告 |
| JSON | 程序处理 |
| JSONL | AI 训练数据 |
| HTML | 本地浏览 |
| PDF | 打印存档 |

### 4. 逐会话 ZIP

借鉴 DeepSeek Exporter，每个对话独立打包：

```bash
python scripts/export.py --per-chat-zip
```

### 5. 标签系统

给对话打标签，方便分类管理：

```bash
python scripts/export.py --tag "技术"
python scripts/export.py --tag "学习"
```

### 6. 限速防风控

可配置请求间隔，避免被 DeepSeek 封禁：

```bash
python scripts/backup.py --rate-limit 3.0  # 3秒间隔
```

### 7. 增量去重

基于 SHA-256 内容哈希，只备份有变化的对话：

```bash
python scripts/backup.py  # 自动跳过未变化的
```

## 快速开始

### 安装

```bash
pip install selenium python-docx markdown pyyaml
```

### 首次登录

```bash
python scripts/backup.py --login
```

### 全量备份

```bash
python scripts/backup.py --full --pii
```

### 定时备份

```bash
python scripts/scheduler.py install-cron  # 每天凌晨2点
```

## 灵感来源

本项目借鉴了 GitHub 上 Top10 的聊天备份项目：

| 项目 | 借鉴的特性 |
|------|-----------|
| DataClaw | PII 脱敏、JSONL 格式 |
| Kept | SQLite FTS5 搜索 |
| DeepSeek Exporter | 逐会话 ZIP |
| Claude Extractor | YAML Front Matter |
| Chat Memo | 标签系统 |
| chatgpt-backup | 客户端脚本设计 |
| chatgpt-exporter | 断点续传、并行下载 |

## 安全保障

- **本地存储**：所有数据不上传任何服务器
- **PII 脱敏**：自动识别并脱敏敏感信息
- **增量备份**：只传输必要的数据
- **登录态保护**：Cookie 和浏览器 profile 加密存储

## GitHub

https://github.com/infanwang/deepseek-backup

欢迎 Star、Fork、Issue！

## License

MIT
