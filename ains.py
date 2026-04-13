#!/usr/bin/env python3
"""
 (All-In-News Skill) - 激进新闻抓取主程序
永不放弃的新闻抓取策略
"""

import os
import sys
import re
import time
import json
import yaml
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, quote_plus

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from strategies.direct_fetch import DirectFetcher
from strategies.keyword_search import KeywordSearcher
from strategies.alternative_finder import AlternativeFinder
from tools.content_fetcher import ContentFetcher
from databases.easy_sites import EasySitesDB
from databases.backup_news import BackupNewsDB

class :
    """主类 - 激进新闻抓取引擎"""
    
    def __init__(self, config_path: str = None):
        """初始化引擎"""
        self.config = self._load_config(config_path)
        self.logs = []
        
        # 初始化组件
        self.direct_fetcher = DirectFetcher(self.config)
        self.keyword_searcher = KeywordSearcher(self.config)
        self.alternative_finder = AlternativeFinder(self.config)
        self.content_fetcher = ContentFetcher(self.config)
        self.easy_sites_db = EasySitesDB()
        self.backup_db = BackupNewsDB()
        
        # 统计信息
        self.stats = {
            "total_attempts": 0,
            "successful_fetches": 0,
            "failed_fetches": 0,
            "alternative_used": 0,
            "backup_used": 0,
            "total_time": 0
        }
    
    def _load_config(self, config_path: str = None) -> Dict:
        """加载配置"""
        default_config = {
            "strategies": {
                "direct_fetch": {
                    "timeout": 5,
                    "max_retries": 2,
                    "enabled": True
                },
                "keyword_search": {
                    "max_keywords": 5,
                    "search_depth": 3,
                    "enabled": True
                },
                "alternative_finder": {
                    "max_alternatives": 10,
                    "enabled": True
                }
            },
            "tools": {
                "web_fetch": {"enabled": True},
                "browser": {"enabled": True},
                "content_fetcher": {"enabled": True}
            },
            "backup": {
                "enabled": True,
                "min_content_length": 100
            },
            "logging": {
                "level": "INFO",
                "file": "ains.log"
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = yaml.safe_load(f)
                    # 合并配置
                    self._merge_config(default_config, user_config)
            except Exception as e:
                self._log(f"加载配置文件失败: {e}", "WARNING")
        
        return default_config
    
    def _merge_config(self, base: Dict, update: Dict):
        """递归合并配置"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _log(self, message: str, level: str = "INFO"):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        self.logs.append(log_entry)
        
        # 控制台输出
        if level in ["INFO", "WARNING", "ERROR"]:
            print(log_entry)
        
        # 文件日志
        log_file = self.config["logging"]["file"]
        if log_file:
            try:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + "\n")
            except:
                pass
    
    def aggressive_fetch(self, url: str, title: str = None) -> Dict:
        """
        激进抓取主函数
        返回: {
            "success": bool,
            "content": str,
            "source": str,  # direct/alternative/backup
            "original_url": str,
            "actual_url": str,
            "attempts": int,
            "time_used": float,
            "logs": List[str]
        }
        """
        start_time = time.time()
        attempts = 0
        batch_logs = []
        
        self._log(f"开始激进抓取: {url}")
        
        result = {
            "success": False,
            "content": "",
            "source": "unknown",
            "original_url": url,
            "actual_url": url,
            "attempts": 0,
            "time_used": 0,
            "logs": []
        }
        
        # 阶段1: 直接抓取
        if self.config["strategies"]["direct_fetch"]["enabled"]:
            self._log("阶段1: 直接抓取")
            content, source_url, attempt_logs = self.direct_fetcher.fetch(url)
            attempts += 1
            batch_logs.extend(attempt_logs)
            
            if content and len(content) > self.config["backup"]["min_content_length"]:
                result.update({
                    "success": True,
                    "content": content,
                    "source": "direct",
                    "actual_url": source_url or url,
                    "attempts": attempts
                })
                self.stats["successful_fetches"] += 1
                self._log(f"✅ 直接抓取成功: {source_url or url}")
                goto_finish = True
                return self._finalize_result(result, start_time, batch_logs)
            else:
                self._log(f"❌ 直接抓取失败，尝试阶段2")
        
        # 阶段2: 关键词搜索转载
        if self.config["strategies"]["keyword_search"]["enabled"]:
            self._log("阶段2: 关键词搜索转载")
            
            # 提取关键词
            keywords = self.keyword_searcher.extract(url, title)
            if keywords:
                self._log(f"提取关键词: {', '.join(keywords[:3])}")
                
                # 搜索转载
                alternative_urls = self.alternative_finder.find(keywords)
                if alternative_urls:
                    self._log(f"找到{len(alternative_urls)}个替代URL")
                    
                    # 尝试每个替代URL
                    for i, alt_url in enumerate(alternative_urls[:5]):  # 最多尝试5个
                        self._log(f"  尝试替代 {i+1}: {alt_url[:60]}...")
                        content, source_url, attempt_logs = self.direct_fetcher.fetch(alt_url)
                        attempts += 1
                        batch_logs.extend(attempt_logs)
                        
                        if content and len(content) > self.config["backup"]["min_content_length"]:
                            result.update({
                                "success": True,
                                "content": content,
                                "source": "alternative",
                                "actual_url": source_url or alt_url,
                                "attempts": attempts
                            })
                            self.stats["successful_fetches"] += 1
                            self.stats["alternative_used"] += 1
                            self._log(f"✅ 替代抓取成功: {source_url or alt_url}")
                            goto_finish = True
                            return self._finalize_result(result, start_time, batch_logs)
            
            self._log(f"❌ 关键词搜索失败，尝试阶段3")
        
        # 阶段3: 易抓取网站搜索
        if self.config["strategies"]["alternative_finder"]["enabled"]:
            self._log("阶段3: 易抓取网站搜索")
            
            # 从易抓取网站数据库寻找
            easy_sites = self.easy_sites_db.get_sites_for_keywords(keywords if keywords else ["news"])
            
            for site_info in easy_sites[:3]:  # 最多尝试3个
                site_url = site_info["url_pattern"].format(
                    keywords[0] if keywords else "news"
                )
                
                self._log(f"  尝试易抓取网站: {site_url[:60]}...")
                content, source_url, attempt_logs = self.direct_fetcher.fetch(site_url)
                attempts += 1
                batch_logs.extend(attempt_logs)
                
                if content and len(content) > self.config["backup"]["min_content_length"]:
                    result.update({
                        "success": True,
                        "content": content,
                        "source": "easy_site",
                        "actual_url": source_url or site_url,
                        "attempts": attempts
                    })
                    self.stats["successful_fetches"] += 1
                    self.stats["alternative_used"] += 1
                    self._log(f"✅ 易抓取网站成功: {source_url or site_url}")
                    goto_finish = True
                    return self._finalize_result(result, start_time, batch_logs)
            
            self._log(f"❌ 易抓取网站搜索失败，进入阶段4")
        
        # 阶段4: 备用内容
        if self.config["backup"]["enabled"]:
            self._log("阶段4: 使用备用内容")
            
            backup_content = self.backup_db.get_backup(keywords)
            if backup_content:
                result.update({
                    "success": True,
                    "content": backup_content,
                    "source": "backup",
                    "actual_url": "backup://" + (keywords[0] if keywords else "default"),
                    "attempts": attempts
                })
                self.stats["successful_fetches"] += 1
                self.stats["backup_used"] += 1
                self._log(f"✅ 使用备用内容")
                goto_finish = True
                return self._finalize_result(result, start_time, batch_logs)
            else:
                self._log(f"❌ 无备用内容，完全失败")
        
        # 所有阶段都失败
        self.stats["failed_fetches"] += 1
        result["attempts"] = attempts
        self._log(f"💀 所有抓取尝试都失败")
        
        return self._finalize_result(result, start_time, batch_logs)
    
    def _finalize_result(self, result: Dict, start_time: float, logs: List[str]) -> Dict:
        """最终化结果"""
        end_time = time.time()
        time_used = end_time - start_time
        
        result.update({
            "time_used": round(time_used, 2),
            "logs": logs
        })
        
        self.stats["total_attempts"] += result["attempts"]
        self.stats["total_time"] += time_used
        
        return result
    
    def batch_fetch(self, urls: List[str], titles: List[str] = None) -> List[Dict]:
        """批量抓取"""
        results = []
        
        self._log(f"开始批量抓取 {len(urls)} 个URL")
        
        for i, url in enumerate(urls):
            title = titles[i] if titles and i < len(titles) else None
            
            self._log(f"处理 {i+1}/{len(urls)}: {url[:60]}...")
            
            result = self.aggressive_fetch(url, title)
            results.append(result)
            
            # 短暂暂停，避免请求过快
            if i < len(urls) - 1:
                time.sleep(0.5)
        
        self._log(f"批量抓取完成，成功 {sum(1 for r in results if r['success'])}/{len(results)}")
        
        return results
    
    def search_news(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索新闻"""
        self._log(f"搜索新闻: {query}")
        
        # 这里应该调用新闻搜索API
        # 简化：返回模拟结果
        mock_results = []
        
        # 构建搜索URL
        search_urls = [
            f"https://news.google.com/search?q={quote_plus(query)}",
            f"https://ground.news/search?q={quote_plus(query)}",
            f"https://www.newsbreak.com/search?q={quote_plus(query)}",
        ]
        
        # 抓取搜索结果
        for search_url in search_urls[:2]:
            result = self.aggressive_fetch(search_url)
            if result["success"]:
                mock_results.append(result)
            
            if len(mock_results) >= limit:
                break
        
        self._log(f"搜索完成，找到 {len(mock_results)} 个结果")
        
        return mock_results
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = self.stats.copy()
        
        if stats["total_attempts"] > 0:
            stats["success_rate"] = stats["successful_fetches"] / stats["total_attempts"] * 100
            stats["avg_time_per_fetch"] = stats["total_time"] / stats["total_attempts"]
        else:
            stats["success_rate"] = 0
            stats["avg_time_per_fetch"] = 0
        
        return stats
    
    def save_results(self, results: List[Dict], output_dir: str = "./output"):
        """保存结果到文件"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 保存为JSON
        json_file = os.path.join(output_dir, f"ains_results_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        # 保存为Markdown
        md_file = os.path.join(output_dir, f"ains_results_{timestamp}.md")
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# 抓取结果 - {timestamp}\n\n")
            
            successful = [r for r in results if r["success"]]
            failed = [r for r in results if not r["success"]]
            
            f.write(f"**总计**: {len(results)} 个URL\n")
            f.write(f"**成功**: {len(successful)} 个\n")
            f.write(f"**失败**: {len(failed)} 个\n")
            f.write(f"**成功率**: {len(successful)/len(results)*100:.1f}%\n\n")
            
            f.write("## 成功抓取\n\n")
            for i, result in enumerate(successful, 1):
                f.write(f"### {i}. {result['original_url'][:80]}...\n")
                f.write(f"- **实际来源**: {result['actual_url']}\n")
                f.write(f"- **抓取策略**: {result['source']}\n")
                f.write(f"- **尝试次数**: {result['attempts']}\n")
                f.write(f"- **用时**: {result['time_used']}秒\n")
                f.write(f"- **内容摘要**: {result['content'][:200]}...\n\n")
            
            if failed:
                f.write("## 失败抓取\n\n")
                for i, result in enumerate(failed, 1):
                    f.write(f"{i}. {result['original_url']}\n")
        
        self._log(f"结果已保存到: {json_file}, {md_file}")
        
        return json_file, md_file

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description=" - 激进新闻抓取技能")
    parser.add_argument("command", choices=["fetch", "batch", "search", "stats"],
                       help="命令: fetch(单个抓取), batch(批量抓取), search(搜索), stats(统计)")
    
    parser.add_argument("--url", help="要抓取的URL（fetch命令使用）")
    parser.add_argument("--title", help="URL的标题（可选）")
    parser.add_argument("--input", help="输入文件（batch命令使用，每行一个URL）")
    parser.add_argument("--query", help="搜索查询（search命令使用）")
    parser.add_argument("--limit", type=int, default=10, help="搜索结果数量限制")
    parser.add_argument("--output-dir", default="./output", help="输出目录")
    parser.add_argument("--config", help="配置文件路径")
    parser.add_argument("--parallel", type=int, default=1, help="并发数（批量抓取时）")
    
    args = parser.parse_args()
    
    # 初始化
    ains = (args.config)
    
    try:
        if args.command == "fetch":
            if not args.url:
                print("错误: fetch命令需要--url参数")
                sys.exit(1)
            
            result = ains.aggressive_fetch(args.url, args.title)
            
            # 输出结果
            print("\n" + "="*60)
            print("抓取结果")
            print("="*60)
            print(f"URL: {result['original_url']}")
            print(f"状态: {'✅ 成功' if result['success'] else '❌ 失败'}")
            print(f"来源: {result['source']}")
            print(f"实际URL: {result['actual_url']}")
            print(f"尝试次数: {result['attempts']}")
            print(f"用时: {result['time_used']}秒")
            print(f"内容长度: {len(result['content'])}字符")
            print("\n内容预览:")
            print("-"*40)
            print(result['content'][:500] + ("..." if len(result['content']) > 500 else ""))
            print("-"*40)
            
            # 保存结果
            ains.save_results([result], args.output_dir)
        
        elif args.command == "batch":
            if not args.input or not