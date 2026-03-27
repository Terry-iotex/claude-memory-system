#!/usr/bin/env python3
"""
从旧 Claude 记忆系统迁移到分层记忆架构
"""
import sys
import shutil
from pathlib import Path

# 旧记忆目录
OLD_MEMORY_DIR = Path.home() / ".claude/projects/-root/memory"

# 新记忆系统目录
NEW_BASE_DIR = Path.home() / ".claude/memory-system"

# 导入管理器
sys.path.insert(0, str(Path(__file__).parent))
from memory_manager import MemoryManager


def migrate():
    """执行迁移"""
    print("=" * 50)
    print("Claude 记忆系统迁移工具")
    print("=" * 50)

    # 检查旧目录
    if not OLD_MEMORY_DIR.exists():
        print(f"\n❌ 旧记忆目录不存在: {OLD_MEMORY_DIR}")
        return False

    # 初始化新系统
    manager = MemoryManager(str(NEW_BASE_DIR))
    print(f"\n✓ 新系统目录: {NEW_BASE_DIR}")

    # 读取旧记忆文件
    old_memories = {}
    for md_file in OLD_MEMORY_DIR.glob("*.md"):
        content = md_file.read_text(encoding='utf-8')
        old_memories[md_file.stem] = content
        print(f"✓ 找到: {md_file.name}")

    if not old_memories:
        print("\n❌ 没有找到记忆文件")
        return False

    # 迁移到核心记忆
    print(f"\n📌 迁移到核心记忆...")

    # MEMORY.md -> 核心
    if "MEMORY" in old_memories:
        manager.add_core("user_info", old_memories["MEMORY"], "identity")
        print("  ✓ MEMORY.md -> user_info")

    # rules.md -> 核心
    if "rules" in old_memories:
        manager.add_core("dev_rules", old_memories["rules"], "rules")
        print("  ✓ rules.md -> dev_rules")

    # projects.md -> 核心
    if "projects" in old_memories:
        manager.add_core("projects", old_memories["projects"], "config")
        print("  ✓ projects.md -> projects")

    # done.md -> 工作记忆（然后归档）
    if "done" in old_memories:
        manager.add_archival(old_memories["done"], {"source": "done.md", "type": "completed_tasks"})
        print("  ✓ done.md -> 档案记忆")

    # 其他文件 -> 档案
    for name, content in old_memories.items():
        if name not in ["MEMORY", "rules", "projects", "done"]:
            manager.add_archival(content, {"source": f"{name}.md"})
            print(f"  ✓ {name}.md -> 档案记忆")

    print("\n" + "=" * 50)
    print("✅ 迁移完成!")
    print("=" * 50)

    # 显示状态
    print("\n新系统状态:")
    manager.status()

    return True


if __name__ == "__main__":
    confirm = input("是否开始迁移? (y/n): ")
    if confirm.lower() == "y":
        migrate()
    else:
        print("已取消")
