#!/usr/bin/env python3
"""
向量检索模块 - 使用 ChromaDB 实现语义搜索
Vector Search Module with ChromaDB Semantic Search

功能：
- 自动向量化记忆内容
- 语义相似度搜索
- 按需检索，减少 token 消耗
"""
import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import chromadb
from chromadb.utils import embedding_functions


class VectorSearch:
    """向量检索引擎"""

    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = Path.home() / ".claude/memory-system"
        self.base_dir = Path(base_dir)

        # 向量数据库目录
        self.chroma_dir = self.base_dir / ".chroma_db"
        self.chroma_dir.mkdir(parents=True, exist_ok=True)

        # 记忆目录
        self.core_dir = self.base_dir / "core"
        self.working_dir = self.base_dir / "working"
        self.obs_dir = self.base_dir / "observational"
        self.archival_dir = self.base_dir / "archival"

        # 初始化 ChromaDB
        self._init_chroma()

    def _init_chroma(self):
        """初始化 ChromaDB 客户端"""
        try:
            # 使用持久化客户端
            self.client = chromadb.PersistentClient(path=str(self.chroma_dir))

            # 使用默认嵌入函数（会尝试使用缓存的模型）
            self.embedding_function = embedding_functions.DefaultEmbeddingFunction()

            # 获取或创建集合
            self.collection = self._get_or_create_collection()

        except Exception as e:
            print(f"警告：ChromaDB 初始化失败: {e}")
            print("提示：首次运行需要下载嵌入模型（~80MB）")
            self.client = None
            self.collection = None

    def _get_or_create_collection(self):
        """获取或创建向量集合"""
        collection_name = "claude_memory"

        try:
            # 尝试获取现有集合
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✓ 使用现有向量库 ({collection.count()} 条记忆)")
            return collection
        except:
            # 创建新集合
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Claude AI 分层记忆向量库"}
            )
            print("✓ 创建新向量库")
            return collection

    def index_memories(self, force: bool = False):
        """
        索引所有记忆到向量数据库

        Args:
            force: 是否强制重建索引
        """
        if not self.client:
            print("错误：ChromaDB 未初始化")
            return

        # 检查是否需要重建
        if not force and self.collection and self.collection.count() > 0:
            print(f"向量库已有 {self.collection.count()} 条记忆")
            print("使用 --force 强制重建索引")
            return

        print("开始索引记忆...")

        memories = []
        ids = []
        metadatas = []

        # 收集所有记忆
        # 1. 核心记忆
        for f in self.core_dir.glob("*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    memories.append(data.get("content", ""))
                    ids.append(f"core_{data['key']}")
                    metadatas.append({
                        "layer": "core",
                        "key": data['key'],
                        "category": data.get('category', 'general')
                    })
            except:
                pass

        # 2. 工作记忆
        for f in self.working_dir.glob("*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    memories.append(data.get("content", ""))
                    ids.append(f"working_{data['id']}")
                    metadatas.append({
                        "layer": "working",
                        "id": data['id'],
                        "created": data.get('created', '')
                    })
            except:
                pass

        # 3. 档案记忆
        for f in self.archival_dir.glob("*.json"):
            try:
                with open(f, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                    memories.append(data.get("content", ""))
                    ids.append(f"archival_{data['id']}")
                    metadatas.append({
                        "layer": "archival",
                        "id": data['id'],
                        "created": data.get('created', '')
                    })
            except:
                pass

        if not memories:
            print("没有找到需要索引的记忆")
            return

        # 删除旧索引（如果强制重建）
        if force:
            try:
                self.client.delete_collection("claude_memory")
                self.collection = self.client.create_collection(
                    name="claude_memory",
                    embedding_function=self.embedding_function
                )
            except:
                pass

        # 添加到向量库
        print(f"正在向量化 {len(memories)} 条记忆...")
        self.collection.add(
            documents=memories,
            ids=ids,
            metadatas=metadatas
        )

        print(f"✓ 索引完成！共 {len(memories)} 条记忆")

    def search(self, query: str, top_k: int = 5, layer: str = None) -> List[Dict]:
        """
        语义搜索记忆

        Args:
            query: 搜索查询
            top_k: 返回结果数量
            layer: 限制搜索层 (core, working, archival, None=全部)

        Returns:
            相关记忆列表，按相似度排序
        """
        if not self.collection:
            print("错误：向量库未初始化")
            return []

        # 构建过滤条件
        where = None
        if layer:
            where = {"layer": layer}

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where=where
            )

            # 格式化结果
            formatted = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    formatted.append({
                        "content": doc,
                        "score": 1 - results['distances'][0][i],  # 转换为相似度
                        "layer": results['metadatas'][0][i].get('layer', 'unknown'),
                        "metadata": results['metadatas'][0][i]
                    })

            return formatted

        except Exception as e:
            print(f"搜索错误: {e}")
            return []

    def status(self):
        """显示向量库状态"""
        print("=" * 50)
        print("向量检索引擎状态")
        print("=" * 50)

        if not self.client:
            print("❌ ChromaDB 未初始化")
            return

        if not self.collection:
            print("❌ 向量集合未创建")
            return

        count = self.collection.count()
        print(f"\n📊 索引记忆数: {count} 条")
        print(f"📂 向量库目录: {self.chroma_dir}")

        # 计算大小
        size = sum(f.stat().st_size for f in self.chroma_dir.rglob('*') if f.is_file())
        size_mb = size / (1024 * 1024)
        print(f"💾 占用空间: {size_mb:.2f} MB")

        print("=" * 50)


def main():
    """命令行接口"""
    import argparse

    parser = argparse.ArgumentParser(description="Claude 记忆向量检索")
    parser.add_argument("command", choices=["search", "index", "status", "reindex"],
                        help="命令")
    parser.add_argument("--query", help="搜索查询")
    parser.add_argument("--top", type=int, default=5, help="返回结果数")
    parser.add_argument("--layer", help="限制搜索层")

    args = parser.parse_args()

    vs = VectorSearch()

    if args.command == "status":
        vs.status()
    elif args.command == "index":
        vs.index_memories()
    elif args.command == "reindex":
        vs.index_memories(force=True)
    elif args.command == "search":
        if not args.query:
            print("错误：搜索需要 --query 参数")
            return
        results = vs.search(args.query, args.top, args.layer)
        print(f"\n🔍 搜索: \"{args.query}\"")
        print(f"找到 {len(results)} 条相关记忆:\n")
        for i, r in enumerate(results, 1):
            score = r['score'] * 100
            layer_icon = {"core": "📌", "working": "🔧", "archival": "📦"}.get(r['layer'], "📄")
            content = r['content'][:150] + "..." if len(r['content']) > 150 else r['content']
            print(f"[{i}] {layer_icon} 相似度 {score:.1f}%")
            print(f"    {content}\n")


if __name__ == "__main__":
    main()
