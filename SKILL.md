---
name: deepseek-backup
description: Automatic backup tool for DeepSeek chat history. Supports full/incremental backup, PII desensitization, rate limiting, date filtering, keyword search, exports to Markdown, Word, PDF, JSON, HTML formats with ZIP archive. Use when user mentions "backup DeepSeek", "export DeepSeek chats", "save DeepSeek conversations", "DeepSeek chat history", or "备份DeepSeek聊天记录".
license: MIT
compatibility: Requires Python 3.10+, Selenium, Chromium browser
metadata:
  author: cloudpeak
  version: 1.3.0
  category: productivity
  tags: [deepseek, backup, chat-history, selenium, automation, export, viewer, security]
---

# DeepSeek Chat Backup

Secure backup for DeepSeek chat conversations with PII desensitization, rate limiting, incremental dedup, date filtering, keyword search, multi-format export (Markdown, Word, PDF, JSON, HTML Viewer), ZIP archive, and conversation statistics.

## Prerequisites

```bash
pip install selenium python-docx markdown pyyaml fpdf2
```

## Security Features

### PII Desensitization

Automatically masks sensitive information in exports:

| Pattern | Example | Masked |
|---------|---------|--------|
| Phone | 13812345678 | 138****5678 |
| Email | test@example.com | te***@example.com |
| ID Card | 110101199001011234 | 110101199****1234 |
| Bank Card | 6222021234567890 | 6222****9012 |
| IP Address | 192.168.1.100 | 192.168.1.xxx |
| API Keys | token=abc123 | token=***REDACTED*** |

Enable with `--pii` flag or set `pii_desensitize: true` in config.

### Rate Limiting

Configurable request interval to avoid being blocked:

```bash
python scripts/backup.py --rate-limit 3.0  # 3 seconds between requests
```

Default: 2.0 seconds. Includes automatic retry with exponential backoff.

### Incremental Dedup

Compares content hash (not just title) to skip unchanged conversations:

```bash
# Only fetches conversations with new/changed content
python scripts/backup.py
```

## Quick Start

### First-time Login

```bash
python scripts/backup.py --login
```

### Full Backup + Export All Formats

```bash
python scripts/backup.py --full
```

### Incremental Backup

```bash
python scripts/backup.py
```

## Export Commands

### List All Conversations

```bash
python scripts/export.py --list
```

### Export by Date Range

```bash
# Export conversations from July 2026
python scripts/export.py --from-date 2026-07-01 --to-date 2026-07-31

# Export only recent week
python scripts/export.py --from-date 2026-07-12
```

### Export by Keyword

```bash
python scripts/export.py --keyword "5G"
python scripts/export.py -k "架构"
```

### Export Specific Conversations

```bash
# By chat ID
python scripts/export.py --chat-id abc123 def456

# List IDs first
python scripts/export.py --list
```

### Choose Export Format

```bash
# Single format
python scripts/export.py --format pdf
python scripts/export.py -f markdown

# Multiple formats
python scripts/export.py -f markdown word pdf

# All formats (default)
python scripts/export.py -f all
```

### Combined Filters

```bash
# PDF export of 5G-related chats from July
python scripts/export.py -f pdf --keyword "5G" --from-date 2026-07-01 --to-date 2026-07-31

# JSON export of specific conversations
python scripts/export.py -f json --chat-id abc123 def456
```

## Export Formats

| Format | Extension | Features |
|--------|-----------|----------|
| `markdown` / `md` | `.md` | Emojis, headers, clean text |
| `word` / `docx` | `.docx` | Formatted headings, colored roles |
| `pdf` | `.pdf` | Page numbers, color-coded roles |
| `json` | `.json` | Machine-readable, full metadata |
| `html` | `.html` | Local web viewer with sidebar, search, dark theme |

## Additional Features

### Conversation Statistics

```bash
python scripts/export.py --stats
```

Shows total chats, messages, word count (user vs AI).

### ZIP Archive

```bash
python scripts/export.py -f all --zip
```

Bundles all exports into a single ZIP file.

### HTML Viewer

```bash
python scripts/export.py -f html
```

Generates a local web app (`html_viewer/index.html`) for browsing conversations with:
- Dark theme sidebar
- Real-time search
- Click-to-view conversations
- Statistics summary

## Scheduled Backup

```bash
python scripts/scheduler.py install-cron    # Daily at 2:00 AM
python scripts/scheduler.py uninstall-cron  # Remove cron job
python scripts/scheduler.py status          # Check status
```

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

## CLI Reference

```
backup.py:
  --full, -f          Full backup (re-scrape all)
  --login             Login and save session
  --pii               Enable PII desensitization
  --rate-limit        Request interval in seconds (default: 2.0)
  --format            Export formats: markdown word pdf json html all
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
  --chat-id           Specific chat IDs (multiple allowed)
  --zip, -z           Create ZIP archive
```

## Output Structure

```
~/deepseek-backups/
├── cookies.json              # Login session (private!)
├── json/                     # Raw chat data
├── exports/                  # Generated files
│   ├── deepseek_backup_xxx.md
│   ├── deepseek_backup_xxx.docx
│   ├── deepseek_backup_xxx.pdf
│   ├── deepseek_backup_xxx.json
│   ├── deepseek_backup_xxx.zip
│   └── html_viewer/
│       └── index.html        # Local web viewer
├── .browser_data/            # Browser profile
└── .backup_state.json        # Backup state
```

## Security Notes

- `cookies.json` contains login credentials - never share
- All data stored locally, no external transmission
- Set permissions: `chmod 700 ~/deepseek-backups`
