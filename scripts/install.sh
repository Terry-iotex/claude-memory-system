#!/bin/bash
# Claude 分层记忆系统 - 一键安装脚本

set -e

echo "========================================"
echo "Claude 分层记忆系统 - 安装"
echo "========================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# 目标目录
TARGET_DIR="$HOME/.claude/memory-system"

# 备份现有目录
if [ -d "$TARGET_DIR" ]; then
    echo "发现现有安装，备份到 $TARGET_DIR.bak"
    mv "$TARGET_DIR" "$TARGET_DIR.bak.$(date +%Y%m%d_%H%M%S)"
fi

# 创建目标目录
echo "创建目录: $TARGET_DIR"
mkdir -p "$TARGET_DIR"

# 复制文件
echo "复制文件..."
cp -r "$BASE_DIR/core" "$TARGET_DIR/" 2>/dev/null || mkdir -p "$TARGET_DIR/core"
cp -r "$BASE_DIR/working" "$TARGET_DIR/" 2>/dev/null || mkdir -p "$TARGET_DIR/working"
cp -r "$BASE_DIR/observational" "$TARGET_DIR/" 2>/dev/null || mkdir -p "$TARGET_DIR/observational"
cp -r "$BASE_DIR/archival" "$TARGET_DIR/" 2>/dev/null || mkdir -p "$TARGET_DIR/archival"
cp -r "$BASE_DIR/scripts" "$TARGET_DIR/"

# 复制配置文件
if [ -f "$BASE_DIR/config.example.json" ]; then
    if [ ! -f "$TARGET_DIR/config.json" ]; then
        cp "$BASE_DIR/config.example.json" "$TARGET_DIR/config.json"
        echo "已创建配置文件: $TARGET_DIR/config.json"
    fi
else
    # 创建默认配置
    cat > "$TARGET_DIR/config.json" << 'EOF'
{
  "core_memory_limit_kb": 50,
  "working_memory_days": 7,
  "observational_compress_days": 30,
  "auto_archive": true,
  "auto_cleanup_days": 90
}
EOF
    echo "已创建默认配置文件"
fi

# 设置执行权限
chmod +x "$TARGET_DIR/scripts"/*.py

# 创建符号链接到主目录（方便访问）
ln -sf "$TARGET_DIR" "$HOME/claude-memory-system" 2>/dev/null || true

echo ""
echo "========================================"
echo "✅ 安装完成!"
echo "========================================"
echo ""
echo "位置: $TARGET_DIR"
echo ""
echo "下一步："
echo "  1. 迁移旧记忆: python3 $TARGET_DIR/scripts/migrate.py"
echo "  2. 查看状态: python3 $TARGET_DIR/scripts/memory_manager.py status"
echo "  3. 搜索记忆: python3 $TARGET_DIR/scripts/memory_manager.py search --query '关键词'"
echo ""
echo "集成到 OpenClaw:"
echo "  python3 $TARGET_DIR/scripts/integrate_openclaw.py"
echo ""
