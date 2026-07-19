# DeepSeek Chat Backup：我如何用 6 个 GitHub 项目的精华，打造最安全的 AI 对话保险箱

> 一篇关于设计思想、借鉴理念和工程实践的技术博文

---

## TL;DR

**DeepSeek Chat Backup** 是一个开源工具，用于自动备份 DeepSeek 聊天记录。它借鉴了 GitHub 上 Top10 聊天备份项目的设计精华，实现了 PII 脱敏、全文搜索、多格式导出等功能。

**GitHub 仓库**: https://github.com/infanwang/deepseek-backup

**如果你觉得有用，请点个 Star ⭐ 和 Watch 👀，这对我很重要！**

---

## 为什么要做这个工具？

我是一个重度 DeepSeek 用户。每天和 AI 的对话越来越多，但 DeepSeek 没有提供官方的导出工具。

我遇到过这些问题：

- 想找之前的对话，翻半天找不到
- 担心账号出问题，聊天记录全丢
- 想把有价值的对话导出保存，却没有好的方案
- 想用 AI 训练自己的数据，却不知道怎么提取

于是我决定做一个工具来解决这些问题。

## 设计思想：站在巨人的肩膀上

在动手之前，我先研究了 GitHub 上 Top10 的聊天备份项目，提取它们的设计精华：

```
┌─────────────────────────────────────────────────────────────┐
│                    设计灵感来源                               │
├─────────────────────────────────────────────────────────────┤
│  DataClaw      → PII 智能脱敏 + JSONL 训练格式              │
│  Kept          → SQLite FTS5 全文搜索                        │
│  DeepSeek Exporter → 逐会话 ZIP + 零依赖设计                │
│  Claude Extractor  → YAML Front Matter 元数据               │
│  Chat Memo     → 标签系统 + 卡片式管理                       │
│  chatgpt-exporter → 断点续传 + 并行下载                      │
└─────────────────────────────────────────────────────────────┘
                    ↓ 融合创新 ↓
┌─────────────────────────────────────────────────────────────┐
│              DeepSeek Chat Backup v1.4                       │
│  PII脱敏 + 限速 + FTS5搜索 + JSONL + 标签 + 多格式导出      │
└─────────────────────────────────────────────────────────────┘
```

## 核心架构

```
┌──────────────────────────────────────────────────────────────┐
│                    用户界面层                                 │
│  backup.py (登录/抓取)  ←→  export.py (导出/搜索)           │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    核心引擎层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  Selenium    │  │  PII 脱敏    │  │  限速控制    │       │
│  │  浏览器自动化 │  │  正则匹配    │  │  重试机制    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  增量去重    │  │  标签管理    │  │  内容哈希    │       │
│  │  SHA-256     │  │  JSON存储    │  │  变更检测    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    导出引擎层                                 │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐    │
│  │  MD    │ │  Word  │ │  JSON  │ │ JSONL  │ │  HTML  │    │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘    │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐               │
│  │  PDF   │ │  ZIP   │ │ Front  │ │ FTS5   │               │
│  │        │ │  Archive│ │ Matter │ │ Search │               │
│  └────────┘ └────────┘ └────────┘ └────────┘               │
└──────────────────────────────────────────────────────────────┘
```

## 六大核心特性详解

### 1. PII 智能脱敏

借鉴 DataClaw 的设计理念，实现了多层级的 PII 检测和脱敏：

```python
# 支持的 PII 模式
PII_PATTERNS = {
    "phone":     r'1[3-9]\d{9}',           # 手机号
    "email":     r'[\w.+-]+@[\w-]+\.[\w.]+', # 邮箱
    "id_card":   r'\d{17}[\dXx]',           # 身份证
    "bank_card": r'\d{16,19}',              # 银行卡
    "ip_addr":   r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP
    "api_key":   r'(token|key|secret|password)=\S+',       # API密钥
}
```

效果示例：
```
原始: 我的手机号是13812345678，邮箱是test@example.com
脱敏: 我的手机号是138****5678，邮箱***@example.com
```

### 2. SQLite FTS5 全文搜索

借鉴 Kept 项目，实现了毫秒级的全文搜索：

```sql
-- FTS5 虚拟表
CREATE VIRTUAL TABLE chat_fts USING fts5(
    chat_id, title, content, role,
    tokenize='unicode61'
);

-- 搜索示例
SELECT DISTINCT chat_id, title, 
       snippet(chat_fts, 2, '<mark>', '</mark>', '...', 32)
FROM chat_fts 
WHERE chat_fts MATCH 'Lambda架构';
```

### 3. JSONL 训练数据格式

借鉴 DataClaw，支持导出为 AI 训练友好的 JSONL 格式：

```jsonl
{"chat_id":"abc","role":"user","content":"什么是Lambda架构？"}
{"chat_id":"abc","role":"assistant","content":"Lambda架构是一种..."}
```

### 4. YAML Front Matter 元数据

借鉴 Claude Extractor，Markdown 导出带结构化元数据：

```markdown
---
title: DeepSeek Chat Backup
date: 2026-07-19
conversations: 100
messages: 500
tags: [deepseek, backup, architecture]
---
```

### 5. 标签系统

借鉴 Chat Memo，支持给对话打标签分类：

```bash
python scripts/export.py --tag "技术"
python scripts/export.py --tag "学习"
```

### 6. 限速防风控

借鉴 DeepSeek Exporter，实现可配置的限速和重试：

```python
class RateLimiter:
    def __init__(self, min_interval=2.0, max_retries=3):
        self.min_interval = min_interval
        self.max_retries = max_retries
    
    def retry(self, func):
        for attempt in range(self.max_retries):
            try:
                self.wait()
                return func()
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep((attempt + 1) * 5)  # 指数退避
```

## 技术栈选择

| 组件 | 技术 | 选择理由 |
|------|------|----------|
| 浏览器自动化 | Selenium | 成熟稳定，支持无头模式 |
| Word 导出 | python-docx | 原生 Word 格式支持 |
| PDF 导出 | fpdf2 | 轻量级，无需外部依赖 |
| 搜索索引 | SQLite FTS5 | 零配置，性能优秀 |
| 数据存储 | JSON | 人类可读，易于处理 |
| 定时任务 | cron | 系统原生，稳定可靠 |

## 使用效果

### 备份速度
- 100 个对话：约 5 分钟
- 单个对话：约 3 秒
- 增量备份：仅抓取变化的对话

### 导出效果
```
~/deepseek-backups/exports/
├── deepseek_backup_20260719.md      (1.9 MB)
├── deepseek_backup_20260719.docx    (573 KB)
├── deepseek_backup_20260719.json    (1.9 MB)
├── deepseek_backup_20260719.jsonl   (2.1 MB)
├── deepseek_backup_20260719.zip     (3.4 MB)
├── deepseek_search_20260719.db      (1.2 MB)
├── html_viewer/index.html           (2.0 MB)
└── per_chat_zips/                   (100 个独立 ZIP)
```

## 未来规划

- [ ] 支持更多 AI 平台（ChatGPT、Claude、Gemini）
- [ ] 语义搜索（基于 Embedding）
- [ ] 对话摘要生成
- [ ] Web UI 界面
- [ ] Docker 部署支持

## 总结

这个项目的核心设计思想是：

1. **站在巨人肩膀上**：借鉴 Top10 项目的优秀设计
2. **安全第一**：PII 脱敏 + 限速 + 本地存储
3. **实用主义**：解决真实问题，不过度设计
4. **渐进增强**：从基础功能到高级特性，逐步迭代

**如果你觉得这个项目有用，请点个 Star ⭐ 和 Watch 👀！**

你的支持是我持续维护的动力。

---

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/infanwang/deepseek-backup.git
cd deepseek-backup

# 安装依赖
pip install selenium python-docx markdown pyyaml fpdf2

# 首次登录
python scripts/backup.py --login

# 安全备份
python scripts/backup.py --full --pii

# 导出所有格式
python scripts/export.py -f all --zip --build-index
```

---

**License**: MIT

**GitHub**: https://github.com/infanwang/deepseek-backup

**欢迎 Star ⭐ 和 Watch 👀！**
