#!/usr/bin/env python3
"""
创建飞书新版文档 (docx/v1)
API: POST /open-apis/docx/v1/documents
文档: https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/create
"""

import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 飞书应用配置
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
BASE_URL = "https://open.feishu.cn/open-apis"


def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """
    获取 tenant_access_token
    
    Args:
        app_id: 飞书应用 ID
        app_secret: 飞书应用密钥
    
    Returns:
        tenant_access_token
    """
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {
        "app_id": app_id,
        "app_secret": app_secret
    }
    
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"获取 token 失败: {result}")
    
    return result["tenant_access_token"]


def create_document(
    title: str,
    folder_token: Optional[str] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建飞书新版文档
    
    Args:
        title: 文档标题（必填）
        folder_token: 文件夹 token（可选）
        app_id: 应用 ID（默认从环境变量读取）
        app_secret: 应用密钥（默认从环境变量读取）
    
    Returns:
        包含 document 信息的字典
    
    示例返回:
        {
            "document": {
                "document_id": "doxcnxxxxxxxxxxxxxxxxxxxx",
                "title": "我的文档"
            }
        }
    """
    # 使用传入的参数或环境变量
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET，请检查 .env 文件或传入参数")
    
    # 获取访问令牌
    token = get_tenant_access_token(app_id, app_secret)
    
    # 构建请求
    url = f"{BASE_URL}/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"title": title}
    if folder_token:
        body["folder_token"] = folder_token
    
    # 发送请求
    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"创建文档失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def get_document_url(document_id: str) -> str:
    """
    根据 document_id 生成文档访问链接
    
    Args:
        document_id: 文档 ID
    
    Returns:
        文档访问链接
    """
    # 新版文档链接格式
    return f"https://www.feishu.cn/docx/{document_id}"


def main():
    """主函数 - 示例用法"""
    print("=" * 60)
    print("飞书新版文档创建工具 (docx/v1)")
    print("=" * 60)
    
    try:
        # 示例 1: 创建文档
        print("\n📄 示例 1: 创建文档")
        result = create_document(title="测试文档")
        
        document = result.get("document", {})
        document_id = document.get("document_id")
        
        print(f"✅ 文档创建成功!")
        print(f"   文档 ID: {document_id}")
        print(f"   标题: {document.get('title')}")
        print(f"   链接: {get_document_url(document_id)}")
        
        # 示例 2: 在指定文件夹创建文档（取消注释使用）
        # print("\n📁 示例 2: 在指定文件夹创建文档")
        # folder_token = "your_folder_token_here"  # 替换为实际的文件夹 token
        # result = create_document(
        #     title="文件夹中的文档",
        #     folder_token=folder_token
        # )
        # document = result.get("document", {})
        # print(f"✅ 文档创建成功!")
        # print(f"   文档 ID: {document.get('document_id')}")
        # print(f"   链接: {get_document_url(document.get('document_id'))}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
