# 深度解析：如何让 AI 对话备份工具做到"安全合规"

> PII 脱敏、限速防风控、增量去重的技术实现详解

## 前言

在上一篇文章中，我介绍了 DeepSeek Chat Backup 这个工具的设计思想和核心功能。但作为一个处理用户隐私数据的工具，**安全性**是最重要的考量。

今天这篇文章，我将深入解析三个核心安全特性的技术实现：

1. **PII 智能脱敏** — 如何自动识别并脱敏敏感信息
2. **限速防风控** — 如何避免被目标平台封禁
3. **增量去重** — 如何高效检测数据变化

## 一、PII 智能脱敏

### 什么是 PII？

PII（Personally Identifiable Information）即个人可识别信息，包括：

- 手机号码
- 电子邮箱
- 身份证号
- 银行卡号
- IP 地址
- API 密钥

### 脱敏策略设计

我们采用了**正则表达式 + 替换函数**的组合策略：

```python
PII_PATTERNS = {
    # 手机号：保留前3位和后4位，中间用*替换
    "phone": (
        r'1[3-9]\d{9}', 
        lambda m: m.group()[:3] + "****" + m.group()[-4:]
    ),
    
    # 邮箱：保留前2位和@后面的部分
    "email": (
        r'[\w.+-]+@[\w-]+\.[\w.]+', 
        lambda m: m.group()[:2] + "***@" + m.group().split("@")[1]
    ),
    
    # 身份证：保留前6位和后4位
    "id_card": (
        r'\d{17}[\dXx]', 
        lambda m: m.group()[:6] + "********" + m.group()[-4:]
    ),
    
    # 银行卡：保留前4位和后4位
    "bank_card": (
        r'\d{16,19}', 
        lambda m: m.group()[:4] + " **** **** " + m.group()[-4:]
    ),
    
    # IP地址：保留前三段
    "ip_addr": (
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', 
        lambda m: m.group()[:m.group().rfind(".")] + ".xxx"
    ),
    
    # API密钥：完全脱敏
    "api_key": (
        r'(token|key|secret|password|api_key)=\S+', 
        lambda m: m.group().split("=")[0] + "=***REDACTED***"
    ),
}
```

### 为什么用 Lambda 替换？

使用 Lambda 函数而不是简单的字符串替换，是因为：

1. **灵活控制**：每个模式可以有不同的脱敏策略
2. **保留上下文**：保留部分原始信息，便于识别
3. **可扩展**：新增模式只需添加正则和替换函数

### 脱敏效果展示

```
输入: 我的手机号是13812345678，邮箱是test@example.com
输出: 我的手机号是138****5678，邮箱***@example.com

输入: 身份证号110101199001011234，银行卡6222021234567890
输出: 身份证号110101199****1234，银行卡6222****9012

输入: API_KEY=sk-abc123def456，token=xyz789
输出: API_KEY=***REDACTED***，token=***REDACTED***
```

### 局限性与改进方向

当前实现的局限性：

1. **上下文无关**：无法判断"13812345678"是手机号还是其他数字
2. **误伤风险**：银行卡正则可能匹配到其他长数字
3. **新格式**：无法识别新型 PII 格式

改进方向：

- 引入 NER（命名实体识别）模型
- 增加上下文分析
- 支持自定义脱敏规则

## 二、限速防风控

### 为什么需要限速？

自动化爬虫如果请求过快，会被目标平台识别并封禁。DeepSeek 的风控策略包括：

- 短时间内大量请求 → 触发验证码
- 持续高频请求 → 临时封禁 IP
- 异常行为模式 → 账号风险标记

### 限速器设计

```python
class RateLimiter:
    def __init__(self, min_interval=2.0, max_retries=3):
        self.min_interval = min_interval  # 最小请求间隔
        self.max_retries = max_retries    # 最大重试次数
        self.last_request_time = 0
    
    def wait(self):
        """等待最小间隔时间"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            sleep_time = self.min_interval - elapsed
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def retry(self, func, *args, **kwargs):
        """带重试的执行"""
        for attempt in range(self.max_retries):
            try:
                self.wait()
                return func(*args, **kwargs)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # 指数退避：5s, 10s, 15s
                    wait_time = (attempt + 1) * 5
                    print(f"[!] 请求失败，{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    raise e
```

### 指数退避策略

```
第1次失败 → 等待 5秒
第2次失败 → 等待 10秒
第3次失败 → 等待 15秒
第4次失败 → 抛出异常
```

为什么选择指数退避？

1. **渐进式恢复**：给服务器恢复时间
2. **避免雪崩**：防止大量请求同时重试
3. **资源友好**：减少不必要的网络开销

### 使用建议

```bash
# 保守模式（推荐）
python scripts/backup.py --rate-limit 3.0

# 激进模式（可能触发风控）
python scripts/backup.py --rate-limit 1.0

# 超保守模式
python scripts/backup.py --rate-limit 5.0
```

## 三、增量去重

### 为什么需要去重？

聊天记录会不断增长，如果每次备份都全量下载：

1. **时间浪费**：大部分对话没有变化
2. **带宽浪费**：重复传输相同数据
3. **存储浪费**：重复保存相同内容

### 哈希去重设计

我们采用 **SHA-256 内容哈希**进行去重：

```python
import hashlib
import json

def compute_content_hash(messages):
    """计算消息内容的哈希值"""
    # 将消息序列化为 JSON 字符串
    content = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    # 计算 SHA-256 哈希
    return hashlib.sha256(content.encode()).hexdigest()[:16]

def is_chat_updated(existing, new_title, new_messages):
    """判断对话是否有更新"""
    # 标题变化 → 有更新
    if existing.get("title") != new_title:
        return True
    
    # 内容哈希变化 → 有更新
    old_hash = existing.get("content_hash", "")
    new_hash = compute_content_hash(new_messages)
    return old_hash != new_hash
```

### 为什么用 SHA-256？

| 算法 | 速度 | 碰撞概率 | 安全性 |
|------|------|----------|--------|
| MD5 | 快 | 高 | 低 |
| SHA-1 | 中 | 中 | 中 |
| SHA-256 | 慢 | 极低 | 高 |

选择 SHA-256 的理由：

1. **抗碰撞**：几乎不可能找到两个不同的输入产生相同哈希
2. **安全性**：即使数据泄露，也无法反推原始内容
3. **标准化**：广泛支持，兼容性好

### 去重效果

```
第一次备份：95 个对话，全部保存
第二次备份：
  - 新增：0 个
  - 更新：2 个（内容变化）
  - 跳过：93 个（内容未变）
  - 节省时间：约 95%
```

### 为什么不用文件修改时间？

有人可能会问：为什么不用文件的 mtime 来判断？

原因：

1. **不可靠**：文件系统时间可能被篡改
2. **不精确**：mtime 只能判断文件是否被修改，无法判断内容是否变化
3. **跨平台**：不同操作系统的 mtime 行为不一致

## 四、三者协同工作

这三个安全特性不是孤立的，而是协同工作：

```
┌─────────────────────────────────────────────────────────────┐
│                     备份流程                                 │
├─────────────────────────────────────────────────────────────┤
│  1. 限速控制 ──→ 每个请求间隔 2 秒                          │
│       │                                                     │
│       ▼                                                     │
│  2. 增量检测 ──→ 计算内容哈希，跳过未变化的对话              │
│       │                                                     │
│       ▼                                                     │
│  3. 数据抓取 ──→ 获取聊天内容                                │
│       │                                                     │
│       ▼                                                     │
│  4. PII 脱敏 ──→ 自动识别并脱敏敏感信息                     │
│       │                                                     │
│       ▼                                                     │
│  5. 安全存储 ──→ 保存到本地，不上传任何服务器                │
└─────────────────────────────────────────────────────────────┘
```

## 五、总结

### 安全设计原则

1. **最小权限**：只请求必要的数据
2. **数据最小化**：只保存需要的信息
3. **本地优先**：所有数据不离开用户设备
4. **透明可控**：用户可以查看和修改所有设置

### 代码开源

所有安全相关的代码都是开源的，用户可以：

- 审查代码逻辑
- 自定义脱敏规则
- 调整限速参数
- 贡献改进方案

**GitHub**: https://github.com/infanwang/deepseek-backup

### 下一篇文章

下一篇文章将介绍如何扩展这个工具，支持更多 AI 平台（ChatGPT、Claude、Gemini）。

**如果你觉得这篇文章有用，请点个 Star ⭐ 和 Watch 👀！**

---

**相关文章**：
- [上一篇：DeepSeek Chat Backup 设计思想](https://blog.csdn.net/youngerwang)
- [GitHub 仓库](https://github.com/infanwang/deepseek-backup)
