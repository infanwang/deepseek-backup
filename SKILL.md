---
name: deepseek-backup
description: Automatic backup tool for DeepSeek chat history. Supports full/incremental backup, date filtering, keyword search, exports to Markdown, Word, PDF, JSON formats. Use when user mentions "backup DeepSeek", "export DeepSeek chats", "save DeepSeek conversations", "DeepSeek chat history", or "备份DeepSeek聊天记录".
license: MIT
compatibility: Requires Python 3.10+, Selenium, Chromium browser
metadata:
  author: cloudpeak
  version: 1.1.0
  category: productivity
  tags: [deepseek, backup, chat-history, selenium, automation, export]
---

# DeepSeek Chat Backup

Backup DeepSeek chat conversations with date filtering, keyword search, and multi-format export (Markdown, Word, PDF, JSON).

## Prerequisites

```bash
pip install selenium python-docx markdown pyyaml fpdf2
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
export_formats:
  - markdown
  - word
  - pdf
  - json
```

## CLI Reference

```
backup.py:
  --full, -f          Full backup (re-scrape all)
  --login             Login and save session
  --format            Export formats: markdown word pdf json all
  --from-date         Start date YYYY-MM-DD
  --to-date           End date YYYY-MM-DD
  --keyword, -k       Filter by title keyword

export.py:
  --list, -l          List all conversations
  --format, -f        Export formats (multiple allowed)
  --from-date         Start date YYYY-MM-DD
  --to-date           End date YYYY-MM-DD
  --keyword, -k       Filter by title keyword
  --chat-id           Specific chat IDs (multiple allowed)
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
│   └── deepseek_backup_xxx.json
├── .browser_data/            # Browser profile
└── .backup_state.json        # Backup state
```

## Security Notes

- `cookies.json` contains login credentials - never share
- All data stored locally, no external transmission
- Set permissions: `chmod 700 ~/deepseek-backups`
