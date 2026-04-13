"""
关键词搜索策略
从URL和标题提取关键词，用于搜索转载
"""

import re
import os
from typing import List, Tuple
from urllib.parse import urlparse

class KeywordSearcher:
    """关键词搜索策略"""
    
    def __init__(self, config: dict):
        self.config = config
        self.max_keywords = config["strategies"]["keyword_search"]["max_keywords"]
        
        # 停用词列表
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'as', 'is', 'are', 'was', 'were', 'be', 'been',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should',
            'can', 'could', 'may', 'might', 'must', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from',
            'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
            'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any',
            'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
            'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's',
            't', 'can', 'will', 'just', 'don', 'should', 'now'
        }
        
        # 中文停用词
        self.chinese_stop_words = {
            '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都',
            '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会',
            '着', '没有', '看', '好', '自己', '这', '那', '但', '什么', '我们',
            '把', '又', '想', '只', '么', '她', '怎么', '呢', '啦', '给', '哇',
            '哦', '啊', '呀', '嘛', '嗯', '呃', '诶'
        }
    
    def extract(self, url: str, title: str = None) -> List[str]:
        """
        从URL和标题提取关键词
        返回: 关键词列表
        """
        keywords = []
        
        # 从URL提取
        url_keywords = self._extract_from_url(url)
        keywords.extend(url_keywords)
        
        # 从标题提取
        if title:
            title_keywords = self._extract_from_title(title)
            keywords.extend(title_keywords)
        
        # 去重和过滤
        keywords = self._filter_keywords(keywords)
        
        # 限制数量
        return keywords[:self.max_keywords]
    
    def _extract_from_url(self, url: str) -> List[str]:
        """从URL提取关键词"""
        keywords = []
        
        try:
            parsed = urlparse(url)
            
            # 从路径提取
            path = parsed.path
            if path:
                # 移除文件扩展名
                path = re.sub(r'\.[a-z]{2,4}$', '', path)
                
                # 分割路径
                parts = re.split(r'[/\-_.]', path)
                
                for part in parts:
                    part = part.strip()
                    if (len(part) > 2 and 
                        not part.isdigit() and
                        not part.startswith('page') and
                        not part.startswith('index') and
                        not part in ['html', 'htm', 'php', 'aspx']):
                        
                        # 检查是否是中文
                        if self._is_chinese(part):
                            keywords.append(part)
                        else:
                            # 英文单词转为小写
                            keywords.append(part.lower())
            
            # 从域名提取
            domain = parsed.netloc
            if domain:
                # 移除www和常见后缀
                domain = re.sub(r'^www\.', '', domain)
                domain = re.sub(r'\.[a-z]{2,3}$', '', domain)
                
                if domain and len(domain) > 2:
                    keywords.append(domain)
        
        except Exception as e:
            # URL解析失败，尝试简单提取
            words = re.findall(r'[a-zA-Z]{3,}|[\u4e00-\u9fff]{2,}', url)
            keywords.extend(words)
        
        return keywords
    
    def _extract_from_title(self, title: str) -> List[str]:
        """从标题提取关键词"""
        keywords = []
        
        if not title:
            return keywords
        
        # 清理标题
        title_clean = re.sub(r'[^\w\s\u4e00-\u9fff]', ' ', title)
        
        # 分割单词
        words = re.findall(r'[a-zA-Z]{3,}|[\u4e00-\u9fff]{2,}', title_clean)
        
        for word in words:
            word_lower = word.lower() if word.isalpha() else word
            
            # 过滤停用词
            if self._is_chinese(word):
                if word not in self.chinese_stop_words:
                    keywords.append(word)
            else:
                if word_lower not in self.stop_words:
                    keywords.append(word_lower)
        
        return keywords
    
    def _filter_keywords(self, keywords: List[str]) -> List[str]:
        """过滤关键词"""
        filtered = []
        seen = set()
        
        for keyword in keywords:
            # 去重
            if keyword in seen:
                continue
            
            # 长度检查
            if len(keyword) < 2:
                continue
            
            # 停用词检查
            keyword_lower = keyword.lower() if keyword.isalpha() else keyword
            if (keyword_lower in self.stop_words or 
                keyword in self.chinese_stop_words):
                continue
            
            # 数字检查
            if keyword.isdigit():
                continue
            
            # 常见无意义词
            if keyword in ['http', 'https', 'com', 'org', 'net', 'www']:
                continue
            
            filtered.append(keyword)
            seen.add(keyword)
        
        return filtered
    
    def _is_chinese(self, text: str) -> bool:
        """检查文本是否包含中文"""
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    def build_search_queries(self, keywords: List[str], title: str = None) -> List[str]:
        """构建搜索查询"""
        queries = []
        
        if not keywords:
            return queries
        
        # 1. 所有关键词组合
        if len(keywords) >= 3:
            queries.append(' '.join(keywords[:3]))
        
        # 2. 前两个关键词
        if len(keywords) >= 2:
            queries.append(' '.join(keywords[:2]))
        
        # 3. 单个重要关键词
        for keyword in keywords[:3]:
            queries.append(keyword)
        
        # 4. 如果有关键词+年份
        current_year = 2026  # 应该动态获取
        for query in queries[:]:  # 复制列表
            queries.append(f"{query} {current_year}")
        
        # 5. 从标题构建（如果有）
        if title:
            # 提取标题中的名词短语
            title_words = title.split()
            if len(title_words) > 3:
                # 取标题的前半部分
                half_title = ' '.join(title_words[:len(title_words)//2])
                queries.append(half_title)
        
        # 去重
        unique_queries = []
        seen = set()
        for query in queries:
            if query not in seen:
                seen.add(query)
                unique_queries.append(query)
        
        return unique_queries[:5]  # 最多5个查询