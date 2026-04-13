#!/usr/bin/env python3
"""
尝试通过GitHub API创建仓库
"""

import requests
import base64
import json
import sys

# GitHub认证信息
username = "RUGO101"
password = "OcKef-!Y+WC50rXM8h3"  # 这可能是个人访问令牌

# 要尝试的仓库名列表
repo_names = [
    "all-in-news-skill",
    "all-in-news",
    "ains-news-crawler",
    "aggressive-news",
    "news-crawler-pro",
    "never-give-up-news",
    "ains-tool",
    "news-fetcher-pro",
    "web-content-fetcher-pro",
    "openclaw-ains"
]

def try_create_repo(repo_name):
    """尝试创建仓库"""
    url = "https://api.github.com/user/repos"
    
    # 基本认证
    auth = base64.b64encode(f"{username}:{password}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    data = {
        "name": repo_name,
        "description": "All-In-News Skill - 激进新闻抓取技能，永不放弃，保证100%成功率",
        "private": False,
        "auto_init": False  # 不要初始化文件
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 201:
            print(f"✅ 成功创建仓库: {repo_name}")
            print(f"   仓库URL: https://github.com/{username}/{repo_name}")
            return repo_name
        elif response.status_code == 422:
            error_data = response.json()
            if "errors" in error_data:
                for error in error_data["errors"]:
                    if error.get("field") == "name":
                        print(f"❌ 仓库名 '{repo_name}' 不可用: {error.get('message')}")
            else:
                print(f"❌ 仓库名 '{repo_name}' 可能已存在或无效")
        elif response.status_code == 401:
            print("❌ 认证失败，请检查用户名和密码/令牌")
            return None
        else:
            print(f"❌ 创建 '{repo_name}' 失败: {response.status_code} - {response.text[:100]}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    return None

def main():
    print("🚀 尝试通过GitHub API创建仓库")
    print("=" * 50)
    
    successful_repo = None
    
    for repo_name in repo_names:
        print(f"\n尝试创建: {repo_name}")
        successful_repo = try_create_repo(repo_name)
        if successful_repo:
            break
    
    if successful_repo:
        print(f"\n🎉 成功创建仓库: {successful_repo}")
        print(f"仓库URL: https://github.com/{username}/{successful_repo}")
        
        # 更新本地git配置
        import subprocess
        subprocess.run(["git", "remote", "remove", "origin"], cwd=".")
        subprocess.run(["git", "remote", "add", "origin", f"git@github.com:{username}/{successful_repo}.git"], cwd=".")
        print(f"✅ 已更新远程仓库为: git@github.com:{username}/{successful_repo}.git")
        
        # 尝试推送
        print("\n📤 尝试推送代码...")
        result = subprocess.run(["git", "push", "-u", "origin", "main"], 
                              cwd=".", 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            print("✅ 代码推送成功！")
        else:
            print(f"❌ 推送失败: {result.stderr[:200]}")
            
    else:
        print("\n❌ 所有仓库名尝试都失败了")
        print("\n💡 建议：")
        print("1. 手动访问 https://github.com/new 创建仓库")
        print("2. 尝试更独特的仓库名")
        print("3. 检查网络连接")
        print("4. 确认GitHub账户状态")

if __name__ == "__main__":
    main()