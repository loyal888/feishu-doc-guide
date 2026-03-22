#!/usr/bin/env python3
"""
获取飞书文档的所有块结构
API: GET /open-apis/docx/v1/documents/{document_id}/blocks
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
    """获取 tenant_access_token"""
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


def get_document_blocks(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取文档的所有块
    
    Args:
        document_id: 文档 ID
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        块列表
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    resp = requests.get(url, headers=headers)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"获取块失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def get_block_children(
    document_id: str,
    block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取块的子块
    
    Args:
        document_id: 文档 ID
        block_id: 块 ID
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        子块列表
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    resp = requests.get(url, headers=headers)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"获取子块失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档块结构查看工具")
    print("=" * 60)
    
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")
    
    try:
        # 获取所有块
        print("\n📥 获取文档块结构...")
        data = get_document_blocks(document_id)
        
        blocks = data.get("items", [])
        print(f"\n✅ 共获取到 {len(blocks)} 个块")
        
        # 打印所有块的结构
        print("\n" + "=" * 60)
        print("块结构详情:")
        print("=" * 60)
        
        for i, block in enumerate(blocks):
            print(f"\n--- 块 {i+1} ---")
            print(f"block_id: {block.get('block_id')}")
            print(f"block_type: {block.get('block_type')}")
            print(f"parent_id: {block.get('parent_id')}")
            
            # 如果是高亮块，获取子块
            if block.get('block_type') == 19:
                print("\n🔍 发现高亮块，获取子块...")
                children_data = get_block_children(document_id, block.get('block_id'))
                children = children_data.get("items", [])
                print(f"子块数量: {len(children)}")
                
                for j, child in enumerate(children):
                    print(f"\n  子块 {j+1}:")
                    print(f"  block_id: {child.get('block_id')}")
                    print(f"  block_type: {child.get('block_type')}")
                    print(f"  完整结构:\n{json.dumps(child, ensure_ascii=False, indent=2)}")
            
            # 打印完整块结构
            print(f"\n完整结构:\n{json.dumps(block, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
