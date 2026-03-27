#!/usr/bin/env python3
"""
Claude 分层记忆管理系统
Layered Memory Architecture for Claude AI

四层架构：
1. Core Memory (<1KB) - 始终加载的关键信息
2. Working Memory (7天) - 最近活跃记忆
3. Observational Log - 压缩的历史记录
4. Archival Memory - 向量数据库，按需检索
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class MemoryManager:
    """分层记忆管理器"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path.home() / ".claude/memory-system"
        self.base_dir = Path(base_dir)

        # 各层目录
        self.core_dir = self.base_dir / "core"
        self.working_dir = self.base_dir / "working"
        self.obs_dir = self.base_dir / "observational"
        self.archival_dir = self.base_dir / "archival"

        # 配置文件
        self.config_file = self.base_dir / "config.json"

        # 创建目录
        self._init_dirs()

        # 加载配置
        self.config = self._load_config()

    def _init_dirs(self):
        """初始化目录结构"""
        for dir_path in [self.core_dir, self.working_dir, self.obs_dir, self.archival_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        """加载配置"""
        default_config = {
            "core_memory_limit_kb": 10,
            "working_memory_days": 7,
            "observational_compress_days": 30,
            "auto_archive": True,
            "auto_cleanup_days": 90
        }

        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                default_config.update(config)
        else:
            self._save_config(default_config)

        return default_config

    def _save_config(self, config: dict):
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

    # ========== 核心记忆 ==========

    def add_core(self, key: str, content: str, category: str = "general") -> bool:
        """
        添加核心记忆（始终加载）

        Args:
            key: 记忆键名
            content: 记忆内容
            category: 分类（identity, config, rules 等）

        Returns:
            是否成功
        """
        # 检查大小限制
        core_size = sum(f.stat().st_size for f in self.core_dir.glob("*.json"))
        if core_size > self.config["core_memory_limit_kb"] * 1024:
            print(f"警告：核心记忆已超过 {self.config['core_memory_limit_kb']}KB 限制")
            return False

        memory_file = self.core_dir / f"{key}.json"
        memory_data = {
            "key": key,
            "content": content,
            "category": category,
            "created": datetime.now().isoformat(),
            "accessed": datetime.now().isoformat()
        }

        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)

        return True

    def get_core(self, key: str = None) -> Dict:
        """
        获取核心记忆

        Args:
            key: 指定键名，None 则返回全部

        Returns:
            记忆内容
        """
        if key:
            memory_file = self.core_dir / f"{key}.json"
            if memory_file.exists():
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 更新访问时间
                    data["accessed"] = datetime.now().isoformat()
                    self._update_accessed(memory_file, data)
                    return data
            return {}
        else:
            # 返回所有核心记忆
            result = {}
            for memory_file in self.core_dir.glob("*.json"):
                with open(memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    result[data["key"]] = data
            return result

    def _update_accessed(self, file_path: Path, data: dict):
        """更新访问时间"""
        data["accessed"] = datetime.now().isoformat()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ========== 工作记忆 ==========

    def add_working(self, content: str, tags: List[str] = None) -> str:
        """
        添加工作记忆（最近7天）

        Args:
            content: 记忆内容
            tags: 标签列表

        Returns:
            记忆ID
        """
        mem_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory_file = self.working_dir / f"{mem_id}.json"

        memory_data = {
            "id": mem_id,
            "content": content,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "accessed": datetime.now().isoformat()
        }

        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)

        return mem_id

    def get_working(self, days: int = None) -> List[Dict]:
        """
        获取工作记忆

        Args:
            days: 最近几天，None 则使用配置值

        Returns:
            记忆列表
        """
        if days is None:
            days = self.config["working_memory_days"]

        cutoff = datetime.now() - timedelta(days=days)
        result = []

        for memory_file in sorted(self.working_dir.glob("*.json"), reverse=True):
            with open(memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                created = datetime.fromisoformat(data["created"])
                if created >= cutoff:
                    result.append(data)
                else:
                    # 超期，归档到观察日志
                    if self.config["auto_archive"]:
                        self._archive_to_observational(data)

        return result

    def _archive_to_observational(self, memory: dict):
        """归档到观察日志"""
        archive_date = datetime.now().strftime("%Y-%m")
        archive_file = self.obs_dir / f"{archive_date}.jsonl"

        with open(archive_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(memory, ensure_ascii=False) + "\n")

        # 删除原文件
        original_file = self.working_dir / f"{memory['id']}.json"
        original_file.unlink()

    # ========== 观察日志 ==========

    def get_observational(self, months: int = 6) -> List[Dict]:
        """
        获取观察日志

        Args:
            months: 最近几个月

        Returns:
            记忆列表
        """
        result = []
        cutoff = datetime.now() - timedelta(days=months * 30)

        for log_file in sorted(self.obs_dir.glob("*.jsonl")):
            # 从文件名提取月份
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = json.loads(line)
                        created = datetime.fromisoformat(data["created"])
                        if created >= cutoff:
                            result.append(data)
            except:
                pass

        return result

    # ========== 档案记忆 ==========

    def add_archival(self, content: str, metadata: dict = None) -> str:
        """
        添加档案记忆（用于向量检索）

        Args:
            content: 记忆内容
            metadata: 元数据

        Returns:
            记忆ID
        """
        mem_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        memory_file = self.archival_dir / f"{mem_id}.json"

        memory_data = {
            "id": mem_id,
            "content": content,
            "metadata": metadata or {},
            "created": datetime.now().isoformat()
        }

        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, ensure_ascii=False, indent=2)

        return mem_id

    # ========== 自动清理 ==========

    def cleanup_old_memories(self, days: int = None):
        """
        清理过期记忆

        Args:
            days: 保留天数，None 则使用配置值
        """
        if days is None:
            days = self.config["auto_cleanup_days"]

        cutoff = datetime.now() - timedelta(days=days)

        # 清理观察日志
        for log_file in self.obs_dir.glob("*.jsonl"):
            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            if file_mtime < cutoff:
                log_file.unlink()
                print(f"已删除过期日志: {log_file.name}")

        # 清理档案记忆
        for archival_file in self.archival_dir.glob("*.json"):
            with open(archival_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                created = datetime.fromisoformat(data["created"])
                if created < cutoff:
                    archival_file.unlink()
                    print(f"已删除过期档案: {archival_file.name}")

    # ========== 搜索功能 ==========

    def search(self, query: str, layer: str = "all") -> List[Dict]:
        """
        搜索记忆（关键词匹配）

        Args:
            query: 搜索关键词
            layer: 搜索层 (core, working, observational, archival, all)

        Returns:
            匹配的记忆列表
        """
        query_lower = query.lower()
        results = []

        def search_in_dir(directory: Path, content_key: str = "content"):
            """在目录中搜索"""
            matches = []
            for file_path in directory.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        content = data.get(content_key, "")
                        if query_lower in content.lower():
                            matches.append(data)
                except:
                    pass
            return matches

        if layer in ["core", "all"]:
            results.extend(search_in_dir(self.core_dir, "content"))
        if layer in ["working", "all"]:
            results.extend(search_in_dir(self.working_dir, "content"))
        if layer in ["observational", "all"]:
            for log_file in self.obs_dir.glob("*.jsonl"):
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            data = json.loads(line)
                            if query_lower in data.get("content", "").lower():
                                results.append(data)
                except:
                    pass
        if layer in ["archival", "all"]:
            results.extend(search_in_dir(self.archival_dir, "content"))

        return results

    # ========== 状态查看 ==========

    def status(self):
        """打印记忆系统状态"""
        print("=" * 50)
        print("Claude 分层记忆系统状态")
        print("=" * 50)

        # 核心记忆
        core_files = list(self.core_dir.glob("*.json"))
        core_size = sum(f.stat().st_size for f in core_files)
        print(f"\n📌 核心记忆: {len(core_files)} 条 ({core_size} 字节)")
        for f in core_files:
            with open(f, 'r', encoding='utf-8') as fp:
                data = json.load(fp)
                print(f"   - {data['key']} ({data['category']})")

        # 工作记忆
        working_files = list(self.working_dir.glob("*.json"))
        print(f"\n🔧 工作记忆: {len(working_files)} 条")

        # 观察日志
        obs_files = list(self.obs_dir.glob("*.jsonl"))
        print(f"\n📊 观察日志: {len(obs_files)} 个月")

        # 档案记忆
        archival_files = list(self.archival_dir.glob("*.json"))
        print(f"\n📦 档案记忆: {len(archival_files)} 条")

        print(f"\n📂 存储目录: {self.base_dir}")
        print("=" * 50)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Claude 分层记忆管理系统")
    parser.add_argument("command", choices=["status", "search", "cleanup", "init"], help="命令")
    parser.add_argument("--query", help="搜索关键词")
    parser.add_argument("--layer", default="all", help="搜索层")

    args = parser.parse_args()

    manager = MemoryManager()

    if args.command == "status":
        manager.status()
    elif args.command == "search":
        if not args.query:
            print("错误: 搜索需要 --query 参数")
            return
        results = manager.search(args.query, args.layer)
        print(f"\n找到 {len(results)} 条相关记忆:")
        for i, r in enumerate(results, 1):
            content = r.get("content", "")[:100]
            print(f"\n[{i}] {content}")
    elif args.command == "cleanup":
        manager.cleanup_old_memories()
    elif args.command == "init":
        print("记忆系统初始化完成!")
        print(f"目录: {manager.base_dir}")


if __name__ == "__main__":
    main()
