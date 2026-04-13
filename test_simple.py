#!/usr/bin/env python3
"""
简单测试
验证技能基本功能
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 测试导入
    from strategies.keyword_search import KeywordSearcher
    from strategies.alternative_finder import AlternativeFinder
    
    print("✅ 模块导入成功")
    
    # 测试配置
    config = {
        "strategies": {
            "keyword_search": {"max_keywords": 5},
            "alternative_finder": {"max_alternatives": 10}
        }
    }
    
    # 测试关键词提取
    print("\n🧪 测试关键词提取...")
    searcher = KeywordSearcher(config)
    
    test_url = "https://apnews.com/article/iran-us-blockade-hormuz-strait-2026"
    test_title = "US to blockade Iran's Hormuz Strait after ceasefire talks fail"
    
    keywords = searcher.extract(test_url, test_title)
    print(f"提取关键词: {keywords}")
    
    if keywords:
        print("✅ 关键词提取成功")
    else:
        print("❌ 关键词提取失败")
    
    # 测试转载查找
    print("\n🧪 测试转载查找...")
    finder = AlternativeFinder(config)
    
    alternatives = finder.find(keywords)
    print(f"找到替代URL: {len(alternatives)}个")
    
    if alternatives:
        print("✅ 转载查找成功")
        for i, url in enumerate(alternatives[:3], 1):
            print(f"  {i}. {url[:80]}...")
    else:
        print("❌ 转载查找失败")
    
    # 测试查询构建
    print("\n🧪 测试搜索查询构建...")
    queries = searcher.build_search_queries(keywords, test_title)
    print(f"构建查询: {queries}")
    
    if queries:
        print("✅ 查询构建成功")
    else:
        print("❌ 查询构建失败")
    
    print("\n🎉 基础功能测试完成！")
    print("技能已准备好使用。")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)