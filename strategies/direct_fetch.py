"""
直接抓取策略
尝试直接抓取URL内容
"""

import time
import random
from typing import Tuple, List, Optional

class DirectFetcher:
    """直接抓取策略"""
    
    def __init__(self, config: dict):
        self.config = config
        self.timeout = config["strategies"]["direct_fetch"]["timeout"]
        self.max_retries = config["strategies"]["direct_fetch"]["max_retries"]
        
        # 工具选择优先级
        self.tool_priority = []
        if config["tools"]["content_fetcher"]["enabled"]:
            self.tool_priority.append("content_fetcher")
        if config["tools"]["web_fetch"]["enabled"]:
            self.tool_priority.append("web_fetch")
        if config["tools"]["browser"]["enabled"]:
            self.tool_priority.append("browser")
    
    def fetch(self, url: str) -> Tuple[Optional[str], Optional[str], List[str]]:
        """
        尝试直接抓取URL
        返回: (内容, 实际URL, 日志列表)
        """
        logs = []
        
        # 根据URL特点选择工具
        tool = self._select_tool(url)
        logs.append(f"选择工具: {tool} for {url[:60]}...")
        
        # 重试机制
        for attempt in range(self.max_retries):
            try:
                logs.append(f"尝试 {attempt+1}/{self.max_retries}")
                
                content, actual_url = self._fetch_with_tool(url, tool)
                
                if content and len(content) > 50:  # 简单内容检查
                    logs.append(f"✅ 抓取成功，长度: {len(content)}字符")
                    return content, actual_url or url, logs
                else:
                    logs.append(f"⚠️ 内容太短或为空: {len(content) if content else 0}字符")
                    
            except Exception as e:
                logs.append(f"❌ 抓取异常: {str(e)[:100]}")
            
            # 重试前等待
            if attempt < self.max_retries - 1:
                wait_time = random.uniform(0.5, 1.5)
                logs.append(f"等待 {wait_time:.1f}秒后重试")
                time.sleep(wait_time)
        
        logs.append(f"💀 所有重试都失败")
        return None, None, logs
    
    def _select_tool(self, url: str) -> str:
        """根据URL选择最佳抓取工具"""
        
        # 检查URL特征
        url_lower = url.lower()
        
        # 微信公众号 - 使用content_fetcher
        if "mp.weixin.qq.com" in url_lower:
            return "content_fetcher"
        
        # Reuters等需要JavaScript的网站
        if any(site in url_lower for site in ["reuters.com", "bloomberg.com", "wsj.com"]):
            return "browser"
        
        # 简单HTML网站
        if any(site in url_lower for site in [".gov", ".edu", "wikipedia.org"]):
            return "web_fetch"
        
        # 默认使用优先级最高的可用工具
        return self.tool_priority[0] if self.tool_priority else "web_fetch"
    
    def _fetch_with_tool(self, url: str, tool: str) -> Tuple[Optional[str], Optional[str]]:
        """使用指定工具抓取"""
        
        if tool == "content_fetcher":
            return self._fetch_with_content_fetcher(url)
        
        elif tool == "web_fetch":
            return self._fetch_with_web_fetch(url)
        
        elif tool == "browser":
            return self._fetch_with_browser(url)
        
        else:
            raise ValueError(f"未知工具: {tool}")
    
    def _fetch_with_content_fetcher(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """使用web-content-fetcher技能"""
        try:
            # 这里应该调用web-content-fetcher技能
            # 简化：返回模拟内容
            return f"内容来自 {url} (通过content_fetcher)", url
        except Exception as e:
            raise Exception(f"content_fetcher失败: {e}")
    
    def _fetch_with_web_fetch(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """使用web_fetch工具"""
        try:
            # 这里应该调用OpenClaw的web_fetch工具
            # 简化：返回模拟内容
            return f"内容来自 {url} (通过web_fetch)", url
        except Exception as e:
            raise Exception(f"web_fetch失败: {e}")
    
    def _fetch_with_browser(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """使用browser工具"""
        try:
            # 这里应该调用OpenClaw的browser工具
            # 简化：返回模拟内容
            return f"内容来自 {url} (通过browser)", url
        except Exception as e:
            raise Exception(f"browser失败: {e}")