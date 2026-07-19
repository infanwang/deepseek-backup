# DeepSeek Chat Backup

[中文](#中文说明) | English

Automatic backup tool for DeepSeek chat history with PII desensitization, rate limiting, full-text search, and multi-format export.

Inspired by [Top 10 GitHub projects](https://github.com/topics/chatgpt-export) for LLM chat backup.

## Features

### Core
- **Session Persistence**: Login once, browser profile saves session
- **Full/Incremental Backup**: SHA-256 content hash dedup
- **Cron Scheduling**: Daily automatic backup

### Security
- **PII Desensitization**: Auto-mask phone, email, ID card, bank card, IP, API keys
- **Rate Limiting**: Configurable request interval with exponential backoff
- **Local Storage**: All data stays on your machine

### Export Formats
| Format | Use Case |
|--------|----------|
| Markdown | Reading, documentation |
| Word | Formal reports |
| JSON | Programmatic access |
| JSONL | AI training data |
| HTML | Local web viewer |
| PDF | Print archive |
| Front Matter | Markdown with YAML metadata |

### Search & Organization
- **SQLite FTS5 Full-text Search**: Fast search across all conversations
- **Tag System**: Categorize conversations
- **Date/Keyword Filtering**: Precise export control

### Archive
- **ZIP Archive**: Bundle all exports
- **Per-conversation ZIP**: Individual ZIP per conversation
- **Conversation Statistics**: Chat/message/word counts

## Installation

```bash
pip install selenium python-docx markdown pyyaml fpdf2

# Chromium browser required
sudo snap install chromium     # Snap (recommended)
sudo apt install chromium-browser  # APT
```

## Quick Start

### 1. First-time Login

```bash
python scripts/backup.py --login
```

### 2. Full Backup with PII Protection

```bash
python scripts/backup.py --full --pii
```

### 3. Export All Formats

```bash
python scripts/export.py -f all --zip --build-index
```

### 4. Search Conversations

```bash
python scripts/export.py --search "Lambda架构"
```

## Commands

### Backup

| Command | Description |
|---------|-------------|
| `backup.py --login` | Login and save session |
| `backup.py --full` | Full backup |
| `backup.py` | Incremental backup |
| `backup.py --pii` | Enable PII desensitization |
| `backup.py --rate-limit 3.0` | Set request interval (seconds) |

### Export

| Command | Description |
|---------|-------------|
| `export.py -f all` | Export all formats |
| `export.py -f jsonl` | Export as JSONL (training data) |
| `export.py -f frontmatter` | Markdown with YAML metadata |
| `export.py --build-index` | Build SQLite search index |
| `export.py --search "query"` | Full-text search |
| `export.py --per-chat-zip` | ZIP per conversation |
| `export.py --tag "tech"` | Filter by tag |
| `export.py --stats` | Show statistics |
| `export.py --zip` | Bundle into ZIP |
| `export.py --list` | List all conversations |

### Scheduler

| Command | Description |
|---------|-------------|
| `scheduler.py install-cron` | Install daily cron (2:00 AM) |
| `scheduler.py uninstall-cron` | Remove cron job |
| `scheduler.py status` | Check status |

## Configuration

Copy `config.example.yaml` to `config.yaml`:

```yaml
backup_dir: ~/deepseek-backups
deepseek_url: https://chat.deepseek.com
pii_desensitize: false
rate_limit_seconds: 2.0
export_formats:
  - markdown
  - word
  - json
  - html
```

## Output Structure

```
~/deepseek-backups/
├── cookies.json              # Login session (private!)
├── json/                     # Raw chat data
├── tags.json                 # Tag definitions
├── exports/
│   ├── deepseek_backup_xxx.md        # Markdown
│   ├── deepseek_backup_xxx.docx      # Word
│   ├── deepseek_backup_xxx.json      # JSON
│   ├── deepseek_backup_xxx.jsonl     # JSONL (training)
│   ├── deepseek_backup_xxx.zip       # ZIP archive
│   ├── deepseek_search_xxx.db        # SQLite FTS5 index
│   ├── html_viewer/index.html        # Web viewer
│   └── per_chat_zips/               # Individual ZIPs
├── .browser_data/            # Browser profile
└── .backup_state.json        # Backup state
```

## PII Desensitization

| Pattern | Example | Masked |
|---------|---------|--------|
| Phone | 13812345678 | 138****5678 |
| Email | test@example.com | te***@example.com |
| ID Card | 110101199001011234 | 110101199****1234 |
| Bank Card | 6222021234567890 | 6222****9012 |
| IP Address | 192.168.1.100 | 192.168.1.xxx |
| API Key | token=abc123 | token=***REDACTED*** |

## Security

- All data stored locally, no external transmission
- PII auto-desensitization in exports
- Configurable rate limiting
- SHA-256 content hash for dedup
- `chmod 700 ~/deepseek-backups` recommended

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cookie expired | Run `backup.py --login` again |
| No chats found | Check login status |
| Cron not running | WSL needs Windows running |
| Search not working | Run `export.py --build-index` first |

---

## 中文说明

### 核心功能

- **安全备份**: PII 脱敏 + 限速防风控 + 增量去重
- **多格式导出**: Markdown / Word / JSON / JSONL / HTML / PDF
- **全文搜索**: SQLite FTS5 索引，毫秒级检索
- **标签管理**: 分类整理对话

### 快速开始

```bash
# 安装依赖
pip install selenium python-docx markdown pyyaml fpdf2

# 首次登录
python scripts/backup.py --login

# 安全备份（PII脱敏 + 限速）
python scripts/backup.py --full --pii --rate-limit 3.0

# 导出所有格式 + 搜索索引
python scripts/export.py -f all --zip --build-index

# 全文搜索
python scripts/export.py --search "关键词"
```

### 灵感来源

借鉴 GitHub Top10 聊天备份项目的设计精华：

| 项目 | 借鉴特性 |
|------|----------|
| DataClaw | PII 脱敏、JSONL 训练格式 |
| Kept | SQLite FTS5 全文搜索 |
| DeepSeek Exporter | 逐会话 ZIP、限速 |
| Claude Extractor | YAML Front Matter 元数据 |
| Chat Memo | 标签系统 |
| chatgpt-exporter | 断点续传、并行下载 |

### 安全保障

- 所有数据本地存储，不上传任何服务器
- PII 自动脱敏（手机/邮箱/身份证/银行卡等）
- 可配置限速，避免被风控
- SHA-256 内容哈希去重

## License

MIT
