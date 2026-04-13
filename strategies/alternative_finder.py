"""
转载查找策略
寻找新闻的替代来源和转载
"""

import random
from typing import List
from urllib.parse import quote_plus

class AlternativeFinder:
    """转载查找策略"""
    
    def __init__(self, config: dict):
        self.config = config
        self.max_alternatives = config["strategies"]["alternative_finder"]["max_alternatives"]
        
        # 易抓取网站数据库
        self.easy_sites = [
            # 新闻聚合平台
            {
                "name": "Ground News",
                "url_pattern": "https://ground.news/search?q={}",
                "searchable": True,
                "reliability": 0.8
            },
            {
                "name": "NewsBreak",
                "url_pattern": "https://www.newsbreak.com/search?q={}",
                "searchable": True,
                "reliability": 0.7
            },
            {
                "name": "AllSides",
                "url_pattern": "https://www.allsides.com/search?q={}",
                "searchable": True,
                "reliability": 0.9
            },
            
            # 区域新闻网站
            {
                "name": "Middle East Eye",
                "url_pattern": "https://www.middleeasteye.net/search?q={}",
                "searchable": True,
                "reliability": 0.8
            },
            {
                "name": "Al-Monitor",
                "url_pattern": "https://www.al-monitor.com/originals/{}",
                "searchable": False,
                "reliability": 0.7
            },
            {
                "name": "Times of Israel",
                "url_pattern": "https://www.timesofisrael.com/topic/{}/",
                "searchable": False,
                "reliability": 0.8
            },
            
            # 国际媒体
            {
                "name": "France 24",
                "url_pattern": "https://www.france24.com/en/tag/{}",
                "searchable": False,
                "reliability": 0.8
            },
            {
                "name": "DW",
                "url_pattern": "https://www.dw.com/en/top-stories/s-{}",
                "searchable": False,
                "reliability": 0.8
            },
            
            # 中文媒体
            {
                "name": "VOA Chinese",
                "url_pattern": "https://www.voachinese.com/z/{}",
                "searchable": False,
                "reliability": 0.7
            },
            {
                "name": "RFA Mandarin",
                "url_pattern": "https://www.rfa.org/mandarin/{}/",
                "searchable": False,
                "reliability": 0.7
            },
            
            # 博客/自媒体
            {
                "name": "Medium",
                "url_pattern": "https://medium.com/tag/{}",
                "searchable": False,
                "reliability": 0.6
            },
            {
                "name": "Substack",
                "url_pattern": "https://substack.com/search/{}",
                "searchable": True,
                "reliability": 0.6
            },
        ]
        
        # 通用搜索网站
        self.search_sites = [
            "https://news.google.com/search?q={}",
            "https://www.bing.com/news/search?q={}",
            "https://duckduckgo.com/?q={}&t=h_&ia=news",
            "https://www.yahoo.com/news/search?p={}",
        ]
    
    def find(self, keywords: List[str]) -> List[str]:
        """
        寻找替代来源
        返回: 替代URL列表
        """
        if not keywords:
            return []
        
        alternative_urls = []
        
        # 1. 搜索网站
        search_urls = self._build_search_urls(keywords)
        alternative_urls.extend(search_urls)
        
        # 2. 易抓取网站
        easy_urls = self._build_easy_site_urls(keywords)
        alternative_urls.extend(easy_urls)
        
        # 3. 通用新闻URL模式
        news_urls = self._build_news_urls(keywords)
        alternative_urls.extend(news_urls)
        
        # 去重和限制数量
        return self._deduplicate_urls(alternative_urls)[:self.max_alternatives]
    
    def _build_search_urls(self, keywords: List[str]) -> List[str]:
        """构建搜索URL"""
        urls = []
        
        # 构建搜索查询
        queries = self._build_queries(keywords)
        
        for query in queries[:2]:  # 最多2个查询
            encoded_query = quote_plus(query)
            
            for site_template in self.search_sites[:3]:  # 最多3个搜索网站
                url = site_template.format(encoded_query)
                urls.append(url)
        
        return urls
    
    def _build_easy_site_urls(self, keywords: List[str]) -> List[str]:
        """构建易抓取网站URL"""
        urls = []
        
        if not keywords:
            return urls
        
        primary_keyword = keywords[0]
        
        for site in self.easy_sites:
            if site["searchable"]:
                # 可搜索的网站
                encoded_keyword = quote_plus(primary_keyword)
                url = site["url_pattern"].format(encoded_keyword)
            else:
                # 不可搜索的网站，使用关键词作为路径
                url = site["url_pattern"].format(primary_keyword.lower().replace(' ', '-'))
            
            urls.append(url)
        
        return urls[:5]  # 最多5个易抓取网站
    
    def _build_news_urls(self, keywords: List[str]) -> List[str]:
        """构建通用新闻URL"""
        urls = []
        
        if not keywords:
            return urls
        
        # 基于关键词构建可能的新闻URL
        primary_keyword = keywords[0].lower().replace(' ', '-')
        
        # 通用新闻URL模式
        patterns = [
            f"https://example-news.com/{primary_keyword}-latest-news",
            f"https://news-site.org/{primary_keyword}-updates",
            f"https://breaking-news.net/{primary_keyword}-2026",
            f"https://international-news.com/{primary_keyword}-coverage",
            f"https://regional-news.com/{primary_keyword}-report",
        ]
        
        urls.extend(patterns)
        
        return urls
    
    def _build_queries(self, keywords: List[str]) -> List[str]:
        """构建搜索查询"""
        queries = []
        
        # 简单查询
        if keywords:
            queries.append(' '.join(keywords[:3]))
            queries.append(' '.join(keywords[:2]))
            queries.append(keywords[0])
        
        # 添加时间限定
        current_year = 2026
        for query in queries[:]:  # 复制列表
            queries.append(f"{query} {current_year}")
            queries.append(f"{query} news")
            queries.append(f"{query} latest")
        
        # 去重
        unique_queries = []
        seen = set()
        for query in queries:
            if query not in seen:
                seen.add(query)
                unique_queries.append(query)
        
        return unique_queries[:5]
    
    def _deduplicate_urls(self, urls: List[str]) -> List[str]:
        """URL去重"""
        unique_urls = []
        seen = set()
        
        for url in urls:
            # 简单规范化
            normalized = url.lower().rstrip('/')
            
            if normalized not in seen:
                seen.add(normalized)
                unique_urls.append(url)
        
        return unique_urls
    
    def get_easy_sites_for_keywords(self, keywords: List[str]) -> List[dict]:
        """获取适合关键词的易抓取网站"""
        if not keywords:
            return []
        
        primary_keyword = keywords[0].lower()
        
        # 根据关键词匹配网站
        matched_sites = []
        
        for site in self.easy_sites:
            # 检查网站是否适合该关键词
            if self._is_site_suitable(site, primary_keyword):
                matched_sites.append(site)
        
        # 按可靠性排序
        matched_sites.sort(key=lambda x: x["reliability"], reverse=True)
        
        return matched_sites[:5]  # 返回前5个
    
    def _is_site_suitable(self, site: dict, keyword: str) -> bool:
        """检查网站是否适合关键词"""
        
        # 简单关键词匹配
        site_name = site["name"].lower()
        
        # 区域匹配
        regional_keywords = ["middle east", "iran", "israel", "china", "europe"]
        regional_sites = ["middle east", "al-monitor", "times of israel", "france", "dw"]
        
        if any(region in keyword for region in regional_keywords):
            if any(region_site in site_name for region_site in regional_sites):
                return True
        
        # 语言匹配
        chinese_keywords = ["中国", "中文", "新华", "人民"]
        chinese_sites = ["voa chinese", "rfa mandarin"]
        
        if any(chinese in keyword for chinese in chinese_keywords):
            if any(chinese_site in site_name for chinese_site in chinese_sites):
                return True
        
        # 通用匹配
        return True  # 默认都适合