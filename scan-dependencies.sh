#!/bin/bash
# Script để quét dependencies tự động từ Python project

echo "=========================================="
echo "🔍 SCAN DEPENDENCIES - PYTHON PROJECT"
echo "=========================================="
echo ""

# Method 1: Đọc từ pyproject.toml (nếu có)
if [ -f "pyproject.toml" ]; then
    echo "📋 Method 1: Đọc từ pyproject.toml"
    echo "-----------------------------------"
    grep -A 20 "^dependencies = \[" pyproject.toml | grep -E '^\s*"[^"]+~=' | sed 's/^[[:space:]]*//' | sed 's/,$//'
    echo ""
fi

# Method 2: Sử dụng pipreqs (cần cài: pip install pipreqs)
echo "📋 Method 2: Sử dụng pipreqs (quét imports từ code)"
echo "-----------------------------------"
if command -v pipreqs &> /dev/null; then
    echo "Đang quét code để tìm imports..."
    pipreqs --print src/ 2>/dev/null | head -20 || echo "Không tìm thấy dependencies"
else
    echo "⚠️  pipreqs chưa được cài đặt"
    echo "   Cài đặt: pip install pipreqs"
    echo "   Sử dụng: pipreqs . --print"
fi
echo ""

# Method 3: Sử dụng pipdeptree (cần cài: pip install pipdeptree)
echo "📋 Method 3: Sử dụng pipdeptree (hiển thị dependency tree)"
echo "-----------------------------------"
if command -v pipdeptree &> /dev/null; then
    pipdeptree --packages $(grep -A 20 "^dependencies = \[" pyproject.toml | grep -E '^\s*"[^"]+~=' | sed 's/^[[:space:]]*"\([^"]*\)~=.*/\1/' | tr '\n' ' ') 2>/dev/null | head -30 || echo "Không thể hiển thị tree"
else
    echo "⚠️  pipdeptree chưa được cài đặt"
    echo "   Cài đặt: pip install pipdeptree"
    echo "   Sử dụng: pipdeptree"
fi
echo ""

# Method 4: Sử dụng grep để tìm imports
echo "📋 Method 4: Quét imports bằng grep (tự động)"
echo "-----------------------------------"
echo "Tìm các import statements trong src/:"
grep -rh "^import \|^from " src/ 2>/dev/null | \
    sed 's/^import //' | \
    sed 's/^from //' | \
    sed 's/ import.*$//' | \
    sed 's/\..*$//' | \
    sort -u | \
    grep -v "^python_service_template" | \
    head -20
echo ""

# Method 5: Sử dụng uv (nếu có)
echo "📋 Method 5: Sử dụng uv (nếu project dùng uv)"
echo "-----------------------------------"
if command -v uv &> /dev/null && [ -f "uv.lock" ]; then
    echo "Project này sử dụng uv, đọc từ uv.lock:"
    uv pip list --format=freeze 2>/dev/null | head -15 || echo "Không thể list với uv"
else
    echo "⚠️  Không tìm thấy uv.lock hoặc uv chưa được cài"
fi
echo ""

# Method 6: Sử dụng pip freeze (nếu có virtualenv)
echo "📋 Method 6: Sử dụng pip freeze (từ virtualenv)"
echo "-----------------------------------"
if [ -d ".venv" ] || [ -d "venv" ]; then
    echo "Tìm thấy virtualenv, có thể dùng: pip freeze"
    echo "Hoặc: source .venv/bin/activate && pip freeze"
else
    echo "⚠️  Không tìm thấy virtualenv"
fi
echo ""

echo "=========================================="
echo "✅ KẾT LUẬN:"
echo "=========================================="
echo "1. Project này đã có pyproject.toml → đọc dependencies từ đó"
echo "2. Nếu muốn quét tự động từ code → dùng pipreqs"
echo "3. Nếu muốn xem dependency tree → dùng pipdeptree"
echo "4. Nếu project dùng uv → đọc từ uv.lock"
echo ""



