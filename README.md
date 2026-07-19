# DeepSeek Chat Backup

[中文](#中文说明) | English

Automatic backup tool for DeepSeek chat history. Supports full/incremental backup, exports to Markdown and Word formats, with cron scheduling.

## Features

- **Session Persistence**: Login once, browser profile saves session
- **Full Backup**: Download all conversations on first run
- **Incremental Backup**: Only fetch new/updated conversations
- **Dual Export**: Generate both Markdown and Word documents
- **Scheduled Backup**: Cron job for daily automatic execution

## Installation

```bash
pip install selenium python-docx markdown pyyaml

# Chromium browser required
sudo snap install chromium     # Snap (recommended)
sudo apt install chromium-browser  # APT
```

## Quick Start

### 1. First-time Login

```bash
python scripts/backup.py --login
```

Opens Chromium browser. Log in to DeepSeek manually. Session is saved automatically.

### 2. Full Backup

```bash
python scripts/backup.py --full
```

### 3. Incremental Backup

```bash
python scripts/backup.py
```

### 4. Schedule Daily Backup

```bash
python scripts/scheduler.py install-cron  # Runs at 2:00 AM daily
```

## Commands

| Command | Description |
|---------|-------------|
| `python scripts/backup.py --login` | Login and save session |
| `python scripts/backup.py --full` | Full backup |
| `python scripts/backup.py` | Incremental backup |
| `python scripts/export.py` | Export to MD + Word |
| `python scripts/scheduler.py install-cron` | Install cron job |
| `python scripts/scheduler.py uninstall-cron` | Remove cron job |
| `python scripts/scheduler.py status` | Check status |

## Configuration

Copy `config.example.yaml` to `config.yaml`:

```yaml
backup_dir: ~/deepseek-backups
deepseek_url: https://chat.deepseek.com
export_formats:
  - markdown
  - word
```

## Output

```
~/deepseek-backups/
├── json/                 # Raw chat data
├── exports/              # Generated MD + Word files
├── cookies.json          # Login session (private!)
├── .browser_data/        # Browser profile
└── .backup_state.json    # Backup state
```

## Security

- All data stored locally, no external transmission
- `cookies.json` contains login credentials - keep private
- Set permissions: `chmod 700 ~/deepseek-backups`

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Cookie expired | Run `python scripts/backup.py --login` again |
| No chats found | Check login status, UI may have changed |
| Cron not running | System must be on (WSL needs Windows running) |

---

## 中文说明

### 功能

- 首次登录保存会话，后续自动使用
- 全量备份所有聊天记录
- 增量备份只抓取新增/更新的对话
- 导出 Markdown 和 Word 格式
- 支持 cron 定时任务

### 快速开始

```bash
# 安装依赖
pip install selenium python-docx markdown pyyaml

# 首次登录（弹出浏览器）
python scripts/backup.py --login

# 全量备份
python scripts/backup.py --full

# 安装定时任务
python scripts/scheduler.py install-cron
```

### 命令参考

| 命令 | 说明 |
|------|------|
| `python scripts/backup.py --login` | 登录并保存会话 |
| `python scripts/backup.py --full` | 全量备份 |
| `python scripts/backup.py` | 增量备份 |
| `python scripts/export.py` | 仅导出 |
| `python scripts/scheduler.py install-cron` | 安装定时任务 |

### 注意事项

- Cookie 有效期约 30 天，过期需重新登录
- WSL 环境下定时任务需 Windows 开机才能执行
- 所有数据本地存储，不上传任何服务器

## License

MIT
