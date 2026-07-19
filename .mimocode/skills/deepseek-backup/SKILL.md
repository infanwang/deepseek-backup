---
name: deepseek-backup
description: DeepSeek 聊天记录备份工作流
---

## DeepSeek 备份工作流

### 步骤 1: 登录
python scripts/backup.py --login

### 步骤 2: 全量备份
python scripts/backup.py --full --pii --rate-limit 2.0

### 步骤 3: 导出
python scripts/export.py -f all --zip --build-index

