#!/bin/bash

# ABNS测试脚本

set -e

echo "🧪 开始测试ALLIN技能"
echo "===================="

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$INSTALL_DIR"

# 测试1: 检查文件结构
echo "测试1: 检查文件结构..."
required_files=(
    "SKILL.md"
    "abns.py"
    "strategies/direct_fetch.py"
    "strategies/keyword_search.py"
    "strategies/alternative_finder.py"
    "config/strategies.yaml"
)

all_good=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ 缺少: $file"
        all_good=false
    fi
done

if [ "$all_good" = true ]; then
    echo "✅ 文件结构检查通过"
else
    echo "❌ 文件结构检查失败"
    exit 1
fi

# 测试2: 运行简单测试
echo -e "\n测试2: 运行Python测试..."
if python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from strategies.keyword_search import KeywordSearcher
    from strategies.alternative_finder import AlternativeFinder
    
    config = {
        'strategies': {
            'keyword_search': {'max_keywords': 5},
            'alternative_finder': {'max_alternatives': 10}
        }
    }
    
    searcher = KeywordSearcher(config)
    keywords = searcher.extract('https://apnews.com/hub/middle-east', 'Middle East News')
    print(f'✅ 关键词提取: {keywords[:3]}')
    
    finder = AlternativeFinder(config)
    alternatives = finder.find(keywords)
    print(f'✅ 找到替代URL: {len(alternatives)}个')
    
    print('✅ Python模块测试通过')
    
except Exception as e:
    print(f'❌ Python测试失败: {e}')
    sys.exit(1)
"; then
    echo "✅ Python测试通过"
else
    echo "❌ Python测试失败"
    exit 1
fi

# 测试3: 运行ABNS命令行测试
echo -e "\n测试3: 命令行接口测试..."
if python3 abns.py --help 2>&1 | grep -q "ABNS"; then
    echo "✅ 命令行接口正常"
else
    echo "❌ 命令行接口异常"
    exit 1
fi

# 测试4: 创建测试输出
echo -e "\n测试4: 创建测试输出..."
TEST_OUTPUT_DIR="$INSTALL_DIR/output/test_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_OUTPUT_DIR"

cat > "$TEST_OUTPUT_DIR/test_urls.txt" << EOF
https://apnews.com/hub/middle-east
https://www.reuters.com/world/middle-east/
https://edition.cnn.com/world/middleeast
