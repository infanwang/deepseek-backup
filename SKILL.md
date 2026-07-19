---
name: deepseek-backup
description: Automatic backup tool for DeepSeek chat history. Supports full/incremental backup, PII desensitization, rate limiting, SQLite FTS5 search, JSONL training format, YAML Front Matter, per-conversation ZIP, tag system, multi-format export. Use when user mentions "backup DeepSeek", "export DeepSeek chats", "save DeepSeek conversations", "DeepSeek chat history", or "备份DeepSeek聊天记录".
license: MIT
compatibility: Requires Python 3.10+, Selenium, Chromium browser
metadata:
  author: cloudpeak
  version: 1.4.0
  category: productivity
  tags: [deepseek, backup, chat-history, selenium, automation, export, viewer, security, search]
---

# DeepSeek Chat Backup

Secure backup for DeepSeek chat conversations with PII desensitization, rate limiting, SQLite FTS5 full-text search, JSONL training format, YAML Front Matter metadata, per-conversation ZIP, tag system, and multi-format export.

Inspired by Top 10 GitHub projects for LLM chat backup.

## Prerequisites

```bash
pip install selenium python-docx markdown pyyaml fpdf2
```

## Security Features

### PII Desensitization

Automatically masks sensitive information:

| Pattern | Example | Masked |
|---------|---------|--------|
| Phone | 13812345678 | 138****5678 |
| Email | test@example.com | te***@example.com |
| ID Card | 110101199001011234 | 110101199****1234 |
| Bank Card | 6222021234567890 | 6222****9012 |
| IP Address | 192.168.1.100 | 192.168.1.xxx |
| API Keys | token=abc123 | token=***REDACTED*** |

```bash
python scripts/backup.py --pii
```

### Rate Limiting

```bash
python scripts/backup.py --rate-limit 3.0  # 3 seconds between requests
```

Default: 2.0s. Includes automatic retry with exponential backoff.

### Incremental Dedup

SHA-256 content hash comparison (not just title):

```bash
python scripts/backup.py  # Skips unchanged conversations
```

## Export Formats

| Format | Command | Use Case |
|--------|---------|----------|
| Markdown | `-f markdown` | Reading, documentation |
| Word | `-f word` | Formal reports |
| JSON | `-f json` | Programmatic access |
| JSONL | `-f jsonl` | AI training data |
| HTML | `-f html` | Local web viewer |
| PDF | `-f pdf` | Print archive |
| Front Matter | `-f frontmatter` | Markdown with YAML metadata |

## Search & Organization

### Full-text Search (SQLite FTS5)

```bash
# Build search index
python scripts/export.py --build-index

# Search conversations
python scripts/export.py --search "Lambda架构"
```

### Tag System

```bash
python scripts/export.py --tag "技术"
python scripts/export.py --tag "学习"
```

### Date/Keyword Filtering

```bash
python scripts/export.py --from-date 2026-07-01 --to-date 2026-07-31
python scripts/export.py -k "5G"
```

## Archive Options

### ZIP Archive

```bash
python scripts/export.py -f all --zip
```

### Per-conversation ZIP

```bash
python scripts/export.py --per-chat-zip
```

## Quick Start

### First-time Login

```bash
python scripts/backup.py --login
```

### Full Backup with PII Protection

```bash
python scripts/backup.py --full --pii --rate-limit 3.0
```

### Export Everything

```bash
python scripts/export.py -f all --zip --build-index --per-chat-zip
```

## CLI Reference

```
backup.py:
  --full, -f          Full backup (re-scrape all)
  --login             Login and save session
  --pii               Enable PII desensitization
  --rate-limit        Request interval in seconds (default: 2.0)
  --format            Export formats: markdown word pdf json jsonl html frontmatter all
  --from-date         Start date YYYY-MM-DD
  --to-date           End date YYYY-MM-DD
  --keyword, -k       Filter by title keyword

export.py:
  --list, -l          List all conversations
  --stats, -s         Show conversation statistics
  --format, -f        Export formats (multiple allowed)
  --from-date         Start date YYYY-MM-DD
  --to-date           End date YYYY-MM-DD
  --keyword, -k       Filter by title keyword
  --tag, -t           Filter by tag
  --chat-id           Specific chat IDs (multiple allowed)
  --search            Full-text search
  --build-index       Build SQLite search index
  --zip               Create ZIP archive
  --per-chat-zip      ZIP per conversation
```

## Configuration

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
├── tags.json                 # Tag definitions
├── json/                     # Raw chat data
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

## Security Notes

- All data stored locally, no external transmission
- PII auto-desensitization in exports
- Configurable rate limiting
- SHA-256 content hash for dedup
- `chmod 700 ~/deepseek-backups` recommended
