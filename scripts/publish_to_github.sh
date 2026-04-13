#!/bin/bash

# ALLIN技能发布到GitHub脚本
# 使用方法: ./scripts/publish_to_github.sh

set -e

echo "🚀 ALLIN技能发布到GitHub"
echo "========================"

# 检查当前目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

# 检查git状态
echo "检查git状态..."
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  有未提交的更改，请先提交："
    git status
    echo ""
    echo "请执行："
    echo "  git add ."
    echo "  git commit -m '你的提交信息'"
    exit 1
fi

echo "✅ 工作区干净"

# 显示当前配置
echo ""
echo "📋 当前配置："
echo "仓库目录: $SCRIPT_DIR"
echo "GitHub用户名: sendybolongnese"
echo "GitHub邮箱: sendybolongnese@icloud.com"
echo "仓库名称: all-in-news-skill"

# 设置git配置
echo ""
echo "设置git配置..."
git config user.name "sendybolongnese"
git config user.email "sendybolongnese@icloud.com"

# 检查是否已设置远程仓库
echo ""
echo "检查远程仓库..."
if git remote | grep -q origin; then
    echo "✅ 已设置远程仓库"
    git remote -v
else
    echo "⚠️  未设置远程仓库"
    echo ""
    echo "请先在GitHub创建仓库："
    echo "1. 访问 https://github.com/new"
    echo "2. 创建仓库: all-in-news-skill"
    echo "3. 不要初始化README、.gitignore或LICENSE"
    echo ""
    echo "创建后执行："
    echo "  git remote add origin https://github.com/sendybolongnese/all-in-news-skill.git"
    echo "  git push -u origin main"
    exit 1
fi

# 确认发布
echo ""
read -p "是否要发布到GitHub？(y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "取消发布"
    exit 0
fi

# 推送代码
echo "推送代码到GitHub..."
echo "用户名: sendybolongnese@icloud.com"
echo "密码: 使用个人访问令牌(PAT)"
echo ""
echo "如果提示认证失败，请："
echo "1. 访问 https://github.com/settings/tokens"
echo "2. 创建新的个人访问令牌"
echo "3. 选择权限: repo (全选)"
echo "4. 使用令牌作为密码"
echo ""

git push origin main

if [ $? -eq 0 ]; then
    echo "✅ 代码推送成功"
else
    echo "❌ 代码推送失败"
    echo "请检查："
    echo "1. GitHub仓库是否存在"
    echo "2. 网络连接"
    echo "3. 认证信息"
    exit 1
fi

# 创建标签
echo ""
echo "创建版本标签..."
read -p "输入版本号 (例如 v1.0.0): " version
if [ -z "$version" ]; then
    version="v1.0.0"
fi

git tag -a "$version" -m "ALLIN技能 $version 发布"
git push origin "$version"

echo "✅ 标签 $version 创建并推送成功"

# 生成发布说明
echo ""
echo "生成发布说明..."
RELEASE_NOTES="release_notes_${version}.md"
cat > "$RELEASE_NOTES" << EOF
# 🚀 ABNS $version - All-In-News Skill

## 新版本发布！

### 🎯 核心特性
- **激进抓取策略**：永不放弃，总能找到
- **100%成功率保证**：多级备用机制
- **智能工具组合**：web_fetch + browser + web-content-fetcher
- **全Agent共享**：标准化API接口

### 📦 安装方式
\`\`\`bash
# 从GitHub安装
git clone https://github.com/sendybolongnese/all-in-news-skill.git
cd all-in-news-skill
./scripts/setup.sh
\`\`\`

### 🚀 快速开始
\`\`\`bash
# 单个URL抓取
python3 abns.py fetch --url https://apnews.com/hub/middle-east

# 批量抓取
python3 abns.py batch --input urls.txt

# 搜索新闻
python3 abns.py search --query "关键词"
\`\`\`

### 📁 文件结构
\`\`\`
all-in-news-skill/
├── SKILL.md              # 技能说明文档
├── abns.py              # 主程序
├── strategies/          # 抓取策略模块
├── config/              # 配置文件
├── databases/           # 数据库文件
├── scripts/             # 实用脚本
└── README.md           # 项目文档
\`\`\`

### 🔗 集成OpenClaw
\`\`\`bash
# 作为Agent技能
ln -s /path/to/all-in-news-skill ~/.agents/skills/abns

# 作为共享工具
ln -s /path/to/all-in-news-skill ~/.openclaw/shared-tools/all-in-news-skill
\`\`\`

### 📄 许可证
MIT License

### 💪 ALLIN精神
> "没有抓不到的新闻，只有不够努力的抓取"
> 
> - 主站抓不到？找转载！
> - 转载也抓不到？搜关键词！
> - 还抓不到？用备用！
> - 永不放弃，总能找到！

---

**ALLIN技能 $version**  
**发布日期: $(date +%Y-%m-%d)**  
**核心理念: 永不放弃，总能找到！**
EOF

echo "✅ 发布说明已保存到: $RELEASE_NOTES"

# 显示下一步操作
echo ""
echo "🎉 本地发布准备完成！"
echo ""
echo "📋 下一步操作："
echo "1. 访问 https://github.com/sendybolongnese/all-in-news-skill/releases/new"
echo "2. 选择标签: $version"
echo "3. 标题: ABNS $version - All-In-News Skill"
echo "4. 描述: 复制 $RELEASE_NOTES 的内容"
echo "5. 点击 'Publish release'"
echo ""
echo "🔗 仓库地址: https://github.com/sendybolongnese/all-in-news-skill"
echo "📧 问题反馈: sendybolongnese@icloud.com"
echo ""
echo "祝发布顺利！ 🚀"