#!/usr/bin/env python3
"""
OpenClaw Agent 集成脚本
自动配置 OpenClaw 使用分层记忆系统
"""
import os
import sys
from pathlib import Path


def integrate_openclaw():
    """集成到 OpenClaw"""

    # OpenClaw workspace 目录
    openclaw_workspace = Path.home() / ".openclaw/workspace"
    if not openclaw_workspace.exists():
        print("❌ OpenClaw workspace 不存在")
        print(f"   期望位置: {openclaw_workspace}")
        return False

    print("=" * 50)
    print("OpenClaw Agent 集成")
    print("=" * 50)

    # 1. 更新 TOOLS.md
    tools_file = openclaw_workspace / "TOOLS.md"
    tools_content = """# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## 🧠 分层记忆系统 (Layered Memory System)

使用 Claude 分层记忆系统管理长期记忆。

### 命令行使用

```bash
# 查看记忆状态
python3 ~/.claude/memory-system/scripts/memory_manager.py status

# 搜索记忆
python3 ~/.claude/memory-system/scripts/memory_manager.py search --query "关键词"

# 清理过期记忆
python3 ~/.claude/memory-system/scripts/memory_manager.py cleanup
```

### Python API

```python
from memory_manager import MemoryManager

manager = MemoryManager()

# 添加核心记忆
manager.add_core("key", "content", "category")

# 添加工作记忆
manager.add_working("content", tags=["tag1"])

# 添加档案记忆
manager.add_archival("content", {"meta": "data"})

# 搜索记忆
results = manager.search("query", layer="all")
```

### 使用场景

- 用户问"之前X是怎么做的？" → 搜索记忆系统
- 需要记住重要信息 → 添加到核心记忆
- 定期维护 → 清理过期记忆

---

Add your local tool notes below this line.
"""

    if tools_file.exists():
        # 检查是否已集成
        existing_content = tools_file.read_text(encoding='utf-8')
        if "分层记忆系统" in existing_content:
            print("✓ TOOLS.md 已包含记忆系统说明")
        else:
            # 备份并更新
            tools_file.write_text(tools_content, encoding='utf-8')
            print("✓ 已更新 TOOLS.md")
    else:
        tools_file.write_text(tools_content, encoding='utf-8')
        print("✓ 已创建 TOOLS.md")

    # 2. 更新 AGENTS.md（添加记忆系统说明）
    agents_file = openclaw_workspace / "AGENTS.md"
    if agents_file.exists():
        existing_content = agents_file.read_text(encoding='utf-8')
        if "分层记忆系统" in existing_content:
            print("✓ AGENTS.md 已包含记忆系统说明")
        else:
            # 在 Memory 部分后添加说明
            memory_note = """

### 🧠 分层记忆系统

当需要查找历史记忆时，使用分层记忆系统：

```bash
python3 ~/.claude/memory-system/scripts/memory_manager.py search --query "关键词"
```

**重要记忆** 应该保存到分层记忆系统，便于跨会话访问。
"""
            updated_content = existing_content + memory_note
            agents_file.write_text(updated_content, encoding='utf-8')
            print("✓ 已更新 AGENTS.md")

    # 3. 创建 Claude Code Skill
    skill_dir = Path.home() / ".claude/skills/memory-system"
    skill_dir.mkdir(parents=True, exist_ok=True)

    skill_content = """# 记忆系统

使用分层记忆系统管理 Claude 的历史记忆。

## 使用方法

查看记忆状态：
```bash
python3 ~/.claude/memory-system/scripts/memory_manager.py status
```

搜索记忆：
```bash
python3 ~/.claude/memory-system/scripts/memory_manager.py search --query "关键词"
```

清理过期记忆：
```bash
python3 ~/.claude/memory-system/scripts/memory_manager.py cleanup
```

## Python API

```python
from memory_manager import MemoryManager

manager = MemoryManager()

# 添加核心记忆
manager.add_core("key", "content", "category")

# 添加工作记忆
manager.add_working("content", tags=["tag1", "tag2"])

# 添加档案记忆
manager.add_archival("content", {"meta": "data"})

# 搜索记忆
results = manager.search("query", layer="all")
```

## 四层架构

| 层级 | 容量 | 用途 |
|------|------|------|
| 核心记忆 | 50KB | 始终加载的关键信息 |
| 工作记忆 | 7天 | 最近活跃的记忆 |
| 观察日志 | 压缩 | 历史记录 |
| 档案记忆 | 无限 | 按需检索 |
"""

    skill_file = skill_dir / "SKILL.md"
    skill_file.write_text(skill_content, encoding='utf-8')
    print("✓ 已创建 Claude Code Skill")

    # 4. 确保脚本有执行权限
    memory_scripts = Path.home() / ".claude/memory-system/scripts"
    if memory_scripts.exists():
        for script in memory_scripts.glob("*.py"):
            os.chmod(script, 0o755)
        print("✓ 已设置脚本执行权限")

    print("")
    print("=" * 50)
    print("✅ 集成完成!")
    print("=" * 50)
    print("")
    print("OpenClaw Agent 现在可以使用分层记忆系统了。")
    print()
    print("测试搜索:")
    print("  python3 ~/.claude/memory-system/scripts/memory_manager.py search --query 'test'")
    print()

    return True


if __name__ == "__main__":
    try:
        integrate_openclaw()
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)
