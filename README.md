# Claude 分层记忆系统

> 让 Claude AI 拥有像人脑一样的分层记忆能力

## 📖 什么是分层记忆架构？

模仿人类大脑的记忆系统，将记忆分为四层：

```
┌─────────────────────────────────────────┐
│          当前对话（始终在上下文）          │
├─────────────────────────────────────────┤
│  核心记忆 (<1KB) + 工作记忆 (7天)        │ ← 自动加载
├─────────────────────────────────────────┤
│  需要回忆？ → 搜索档案记忆（向量检索）    │ ← 按需获取
└─────────────────────────────────────────┘
```

### 四层架构

| 层级 | 容量 | 加载方式 | 内容举例 |
|------|------|----------|----------|
| **核心记忆** | <1KB | 始终加载 | 名字、邮箱、关键规则 |
| **工作记忆** | 7天 | 始终加载 | 当前任务、最近对话 |
| **观察日志** | 压缩 | 按需加载 | 完成的任务、历史决策 |
| **档案记忆** | 无限 | 按需检索 | 所有历史、语义搜索 |

## 🚀 快速开始

### 一键安装

```bash
curl -sSL https://raw.githubusercontent.com/Terry-iotex/claude-memory-system/main/install.sh | bash
```

### 手动安装

```bash
# 克隆仓库
git clone https://github.com/Terry-iotex/claude-memory-system.git
cd claude-memory-system

# 运行安装脚本
./scripts/install.sh
```

### 从旧记忆迁移

```bash
python3 ~/.claude/memory-system/scripts/migrate.py
```

这会将你现有的 Claude 记忆自动迁移到新系统。

## 📚 基本使用

### 命令行

```bash
# 查看状态
python3 ~/.claude/memory-system/scripts/memory_manager.py status

# 搜索记忆
python3 ~/.claude/memory-system/scripts/memory_manager.py search --query "按钮"

# 清理过期记忆
python3 ~/.claude/memory-system/scripts/memory_manager.py cleanup
```

### Python API

```python
from memory_manager import MemoryManager

# 初始化
manager = MemoryManager()

# 添加核心记忆（始终加载）
manager.add_core("user_name", "Terry", "identity")
manager.add_core("dev_rules", "使用 TypeScript", "rules")

# 添加工作记忆（7天有效）
mem_id = manager.add_working("正在开发 web-tester 项目", tags=["project", "web-tester"])

# 添加档案记忆（永久存储）
archive_id = manager.add_archival("按钮检测问题的解决方法...", {"project": "web-tester"})

# 搜索记忆
results = manager.search("按钮检测", layer="all")

# 获取核心记忆
core = manager.get_core()  # 获取全部
user_name = manager.get_core("user_name")  # 获取单个

# 获取最近工作记忆
working = manager.get_working(days=7)

# 清理过期记忆
manager.cleanup_old_memories(days=90)
```

## 🤖 集成到 AI 工具

### Claude Code 集成

在 `~/.claude/projects/-root/memory/MEMORY.md` 中添加：

```markdown
## 🧠 分层记忆系统

使用分层记忆系统管理历史记忆：

```bash
# 搜索记忆
python3 ~/.claude/memory-system/scripts/memory_manager.py search --query "关键词"
```
```

### OpenClaw 集成

```bash
# 运行 OpenClaw 集成脚本
python3 ~/.claude/memory-system/scripts/integrate_openclaw.py
```

这会自动：
- 更新 `~/.openclaw/workspace/TOOLS.md` 添加工具说明
- 更新 `~/.openclaw/workspace/AGENTS.md` 添加使用指南
- 创建 Claude Code Skill 集成

手动集成步骤：

1. 编辑 `~/.openclaw/workspace/TOOLS.md`，添加：

```markdown
## 🧠 分层记忆系统

### 命令
```bash
python3 ~/.claude/memory-system/scripts/memory_manager.py search --query "关键词"
```
```

2. 编辑 `~/.openclaw/workspace/AGENTS.md`，在 Memory 部分添加说明

## ⚙️ 配置

编辑 `~/.claude/memory-system/config.json`:

```json
{
  "core_memory_limit_kb": 50,
  "working_memory_days": 7,
  "observational_compress_days": 30,
  "auto_archive": true,
  "auto_cleanup_days": 90
}
```

## 📁 目录结构

```
~/.claude/memory-system/
├── core/              # 核心记忆（JSON 文件）
├── working/           # 工作记忆（7天，自动归档）
├── observational/     # 观察日志（按月压缩）
├── archival/          # 档案记忆（可向量检索）
├── scripts/           # 工具脚本
│   ├── memory_manager.py
│   ├── migrate.py
│   ├── install.sh
│   └── integrate_openclaw.py
└── config.json        # 配置文件
```

## 🎯 核心优势

1. **节省 Token** - 不用每次都加载全部历史
2. **快速访问** - 常用信息始终在手边
3. **深度回忆** - 旧记忆通过搜索找回
4. **自动整理** - 过期内容自动归档
5. **多平台兼容** - Claude Code, OpenClaw, 其他 AI 工具

## 🔄 在另一台电脑上使用

### 1. 克隆仓库并安装

```bash
git clone https://github.com/Terry-iotex/claude-memory-system.git
cd claude-memory-system
./scripts/install.sh
```

### 2. 如果有旧记忆，迁移

```bash
python3 ~/.claude/memory-system/scripts/migrate.py
```

### 3. 集成到 OpenClaw（如果使用）

```bash
python3 ~/.claude/memory-system/scripts/integrate_openclaw.py
```

### 4. 同步记忆（可选）

如果你想在多台电脑间同步记忆：

```bash
# 使用 git 同步
cd ~/.claude/memory-system
git init
git remote add origin <你的远程仓库>
git add -A && git commit -m "记忆同步"
git push
```

## 📝 开发计划

- [x] 基础分层记忆系统
- [x] OpenClaw 集成
- [x] Claude Code Skill 集成
- [ ] 向量检索集成（ChromaDB + sentence-transformers）
- [ ] Observer Agent 自动压缩
- [ ] 自动语义归档
- [ ] 多设备同步

## 📄 许可证

MIT License

## 👤 作者

Terry - https://github.com/Terry-iotex

---

**让 AI 拥有持久记忆，让每一次对话都有意义。**
