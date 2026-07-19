---
name: deepseek-backup
description: Automatic backup tool for DeepSeek chat history. Supports full and incremental backup, exports to Markdown and Word formats. Use when user mentions "backup DeepSeek", "export DeepSeek chats", "save DeepSeek conversations", "DeepSeek chat history", or "备份DeepSeek聊天记录".
license: MIT
compatibility: Requires Python 3.10+, Selenium, Chromium browser
metadata:
  author: cloudpeak
  version: 1.0.0
  category: productivity
  tags: [deepseek, backup, chat-history, selenium, automation]
---

# DeepSeek Chat Backup

Automatically backup DeepSeek chat conversations with full/incremental modes, exporting to Markdown and Word formats.

## Prerequisites

```bash
pip install selenium python-docx markdown pyyaml
# Chromium browser required (snap or apt)
```

## Quick Start

### First-time Login

Opens browser for manual login, saves session for future use:

```bash
python scripts/backup.py --login
```

### Full Backup

```bash
python scripts/backup.py --full
```

### Incremental Backup

```bash
python scripts/backup.py
```

### Export Only

```bash
python scripts/export.py
```

### Scheduled Backup (cron)

```bash
python scripts/scheduler.py install-cron    # Daily at 2:00 AM
python scripts/scheduler.py uninstall-cron  # Remove cron job
python scripts/scheduler.py status          # Check status
```

## Configuration

Copy `config.example.yaml` to `config.yaml` and customize:

```yaml
backup_dir: ~/deepseek-backups
deepseek_url: https://chat.deepseek.com
export_formats:
  - markdown
  - word
```

## Output Structure

```
~/deepseek-backups/
├── cookies.json              # Login session (keep private!)
├── json/                     # Raw chat data
│   └── chat_id_title.json
├── exports/                  # Generated files
│   ├── deepseek_backup_xxx.md
│   └── deepseek_backup_xxx.docx
├── .browser_data/            # Browser profile
├── .backup_state.json        # Backup state
└── backup.log                # Cron log
```

## How It Works

1. **Login**: Opens Chromium, user logs in manually, session saved to `cookies.json` and `.browser_data/`
2. **Scrape**: Selenium navigates chat list, extracts messages via JavaScript
3. **Dedup**: Compares chat IDs against existing JSON files, skips unchanged
4. **Export**: Generates Markdown (with emojis) and Word (with formatting) files
5. **Schedule**: Cron runs daily, uses saved session for headless operation

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Cookie expired | Run `python scripts/backup.py --login` again |
| No chats found | Check if logged in, DeepSeek UI may have changed |
| Cron not running | Ensure WSL/Windows is on; cron only runs when system is active |
| Export empty | Run backup first, check `json/` directory |

## Security Notes

- `cookies.json` contains login credentials - never share
- `.browser_data/` contains browser session - keep private
- All data stored locally, no external transmission
- Set permissions: `chmod 700 ~/deepseek-backups`
