#!/bin/bash

# ABNS技能安装脚本

set -e

echo "🚀 开始安装ABNS (All-But-News Skill)"
echo "======================================"

# 检查Python版本
echo "检查Python版本..."
python3 --version || { echo "❌ 需要Python 3.7+"; exit 1; }

# 安装目录
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "安装目录: $INSTALL_DIR"

# 创建必要的目录
echo "创建目录结构..."
mkdir -p "$INSTALL_DIR/strategies"
mkdir -p "$INSTALL_DIR/tools"
mkdir -p "$INSTALL_DIR/databases"
mkdir -p "$INSTALL_DIR/config"
mkdir -p "$INSTALL_DIR/scripts"
mkdir -p "$INSTALL_DIR/output"
mkdir -p "$INSTALL_DIR/logs"

# 检查是否已安装web-content-fetcher
echo "检查依赖技能..."
FETCHER_DIR="$HOME/.agents/skills/web-content-fetcher"
if [ -d "$FETCHER_DIR" ]; then
    echo "✅ 找到web-content-fetcher技能"
else
    echo "⚠️ 未找到web-content-fetcher技能"
    echo "  建议安装以获得最佳效果"
fi

# 安装Python依赖
echo "安装Python依赖..."
cd "$INSTALL_DIR"

if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
else
    # 创建基础requirements.txt
    cat > requirements.txt << EOF
# ABNS基础依赖
PyYAML>=6.0
requests>=2.28.0
beautifulsoup4>=4.11.0
lxml>=4.9.0
html2text>=2020.1.16
EOF
    
    pip3 install -r requirements.txt
fi

# 创建默认配置文件
echo "创建默认配置..."
if [ ! -f "$INSTALL_DIR/config/strategies.yaml" ]; then
    cat > "$INSTALL_DIR/config/strategies.yaml" << EOF
# ABNS策略配置

strategies:
  direct_fetch:
    timeout: 5
    max_retries: 2
    enabled: true
    
  keyword_search:
    max_keywords: 5
    search_depth: 3
    enabled: true
    
  alternative_finder:
    max_alternatives: 10
    enabled: true

tools:
  web_fetch:
    enabled: true
    
  browser:
    enabled: true
    
  content_fetcher:
    enabled: true

backup:
  enabled: true
  min_content_length: 100

logging:
  level: INFO
  file: "$INSTALL_DIR/logs/abns.log"
EOF
    echo "✅ 创建策略配置文件"
fi

# 创建数据库文件
echo "初始化数据库..."
if [ ! -f "$INSTALL_DIR/databases/easy_sites.json" ]; then
    cat > "$INSTALL_DIR/databases/easy_sites.json" << EOF
[
  {
    "name": "Ground News",
    "url_pattern": "https://ground.news/search?q={}",
    "searchable": true,
    "reliability": 0.8,
    "category": "news_aggregator"
  },
  {
    "name": "NewsBreak",
    "url_pattern": "https://www.newsbreak.com/search?q={}",
    "searchable": true,
    "reliability": 0.7,
    "category": "news_aggregator"
  },
  {
    "name": "Middle East Eye",
    "url_pattern": "https://www.middleeasteye.net/search?q={}",
    "searchable": true,
    "reliability": 0.8,
    "category": "regional_news"
  }
]
EOF
    echo "✅ 创建易抓取网站数据库"
fi

if [ ! -f "$INSTALL_DIR/databases/backup_news.json" ]; then
    cat > "$INSTALL_DIR/databases/backup_news.json" << EOF
{
  "default": "备用新闻内容：今日国际新闻摘要待更新。",
  "iran": "伊朗相关新闻：中东地区局势持续紧张。",
  "china": "中国相关新闻：国际关系与经济动态。",
  "usa": "美国相关新闻：政治与经济最新进展。",
  "middle_east": "中东新闻：地区冲突与国际调解。"
}
EOF
    echo "✅ 创建备用新闻数据库"
fi

# 设置执行权限
echo "设置执行权限..."
chmod +x "$INSTALL_DIR/abns.py"
chmod +x "$INSTALL_DIR/scripts/"*.sh 2>/dev/null || true

# 创建符号链接到OpenClaw技能目录
echo "创建OpenClaw技能链接..."
OPENCLAW_SKILLS_DIR="$HOME/.agents/skills"
if [ -d "$OPENCLAW_SKILLS_DIR" ]; then
    ln -sfn "$INSTALL_DIR" "$OPENCLAW_SKILLS_DIR/abns"
    echo "✅ 创建技能链接: $OPENCLAW_SKILLS_DIR/abns"
else
    echo "⚠️ 未找到OpenClaw技能目录，跳过链接创建"
fi

# 创建共享工具链接
echo "创建共享工具链接..."
SHARED_TOOLS_DIR="$HOME/.openclaw/shared-tools"
if [ -d "$SHARED_TOOLS_DIR" ]; then
    ln -sfn "$INSTALL_DIR" "$SHARED_TOOLS_DIR/abns-skill"
    echo "✅ 创建共享工具链接: $SHARED_TOOLS_DIR/abns-skill"
else
    mkdir -p "$SHARED_TOOLS_DIR"
    ln -sfn "$INSTALL_DIR" "$SHARED_TOOLS_DIR/abns-skill"
    echo "✅ 创建共享工具目录和链接"
fi

# 测试安装
echo "测试安装..."
cd "$INSTALL_DIR"
if python3 -c "import yaml, json, re, urllib.parse; print('✅ Python依赖检查通过')"; then
    echo "✅ 基础依赖检查通过"
else
    echo "❌ Python依赖检查失败"
    exit 1
fi

# 创建测试脚本
cat > "$INSTALL_DIR/scripts/test_abns.sh" << 'EOF'
#!/bin/bash

# ABNS测试脚本

set -e

echo "🧪 开始测试ABNS技能"
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
EOF

echo "测试URL已保存到: $TEST_OUTPUT_DIR/test_urls.txt"
echo "✅ 测试环境准备完成"

echo -e "\n🎉 ABNS技能安装测试完成！"
echo "下一步:"
echo "1. 运行完整测试: python3 abns.py fetch --url https://apnews.com/hub/middle-east"
echo "2. 查看技能文档: cat SKILL.md | head -50"
echo "3. 配置个性化设置: 编辑 config/strategies.yaml"
EOF

chmod +x "$INSTALL_DIR/scripts/test_abns.sh"

# 创建cron job脚本
cat > "$INSTALL_DIR/scripts/cron_abns.sh" << 'EOF'
#!/bin/bash

# ABNS定时抓取脚本
# 适合添加到cron job

set -e

echo "🕒 ABNS定时抓取开始: $(date)"
echo "=============================="

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$INSTALL_DIR"

# 日期标记
DATE_TAG=$(date +%Y%m%d_%H%M%S)
TODAY=$(date +%Y-%m-%d)

# 输出目录
OUTPUT_DIR="$INSTALL_DIR/output/daily/$TODAY"
mkdir -p "$OUTPUT_DIR"
mkdir -p "$INSTALL_DIR/logs/daily"

# 日志文件
LOG_FILE="$INSTALL_DIR/logs/daily/abns_${DATE_TAG}.log"

# 要抓取的URL列表
URLS_FILE="$INSTALL_DIR/config/daily_urls.txt"
if [ ! -f "$URLS_FILE" ]; then
    # 创建默认URL列表
    cat > "$URLS_FILE" << URLS
https://apnews.com/hub/middle-east
https://www.reuters.com/world/middle-east/
https://edition.cnn.com/world/middleeast
https://www.bbc.com/news/world/middle_east
https://www.aljazeera.com/middle-east/
URLS
    echo "创建默认URL列表: $URLS_FILE"
fi

echo "开始抓取 $(cat "$URLS_FILE" | wc -l) 个URL..."

# 运行ABNS批量抓取
python3 abns.py batch \
    --input "$URLS_FILE" \
    --output-dir "$OUTPUT_DIR" \
    --parallel 3 \
    2>&1 | tee "$LOG_FILE"

# 检查结果
SUCCESS_COUNT=$(grep -c "✅" "$LOG_FILE" || true)
FAIL_COUNT=$(grep -c "❌" "$LOG_FILE" || true)

echo -e "\n📊 抓取统计:"
echo "成功: $SUCCESS_COUNT"
echo "失败: $FAIL_COUNT"
echo "总计: $(cat "$URLS_FILE" | wc -l)"

# 生成摘要报告
REPORT_FILE="$OUTPUT_DIR/summary_${DATE_TAG}.md"
{
    echo "# ABNS每日抓取报告 - $TODAY"
    echo ""
    echo "**抓取时间**: $(date)"
    echo "**URL数量**: $(cat "$URLS_FILE" | wc -l)"
    echo "**成功数量**: $SUCCESS_COUNT"
    echo "**失败数量**: $FAIL_COUNT"
    echo "**成功率**: $(echo "scale=1; $SUCCESS_COUNT * 100 / $(cat "$URLS_FILE" | wc -l)" | bc)%"
    echo ""
    echo "## 详细日志"
    echo ""
    tail -20 "$LOG_FILE"
} > "$REPORT_FILE"

echo "报告已保存: $REPORT_FILE"
echo "✅ ABNS定时抓取完成: $(date)"
EOF

chmod +x "$INSTALL_DIR/scripts/cron_abns.sh"

echo -e "\n🎉 ABNS技能安装完成！"
echo "======================================"
echo "安装目录: $INSTALL_DIR"
echo "技能文档: $INSTALL_DIR/SKILL.md"
echo "主程序: $INSTALL_DIR/abns.py"
echo ""
echo "📋 可用命令:"
echo "  测试安装: $INSTALL_DIR/scripts/test_abns.sh"
echo "  单个抓取: python3 $INSTALL_DIR/abns.py fetch --url <URL>"
echo "  批量抓取: python3 $INSTALL_DIR/abns.py batch --input <文件>"
echo "  搜索新闻: python3 $INSTALL_DIR/abns.py search --query \"关键词\""
echo ""
echo "🔗 技能已链接到:"
echo "  OpenClaw技能: ~/.agents/skills/abns"
echo "  共享工具: ~/.openclaw/shared-tools/abns-skill"
echo ""
echo "🚀 开始使用ABNS，永不放弃的新闻抓取！"