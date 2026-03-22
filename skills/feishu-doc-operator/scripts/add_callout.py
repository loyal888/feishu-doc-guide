#!/usr/bin/env python3
"""
向飞书文档添加高亮块 (Callout)
根据实际读取的结构创建

步骤：
1. 创建空的高亮块（使用数字颜色值）- 会自动创建一个空子块
2. 获取高亮块 ID 和子块 ID
3. 更新子块的内容（而不是添加新子块）
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
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


def add_blocks_to_document(
    document_id: str,
    blocks: List[Dict[str, Any]],
    block_id: Optional[str] = None,
    index: Optional[int] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """向文档添加块"""
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    parent_block_id = block_id or document_id
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{parent_block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {"children": blocks}
    if index is not None:
        body["index"] = index
    
    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"添加块失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def update_block_text(
    document_id: str,
    block_id: str,
    content: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    更新文本块内容
    API: PATCH /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}
    
    使用 update_text_elements 请求体
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 使用 update_text_elements 请求体
    body = {
        "update_text_elements": {
            "elements": [
                {
                    "type": "text_run",
                    "text_run": {
                        "content": content,
                        "text_element_style": {}
                    }
                }
            ]
        }
    }
    
    resp = requests.patch(url, headers=headers, json=body)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"更新块失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def get_block_children(
    document_id: str,
    block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """获取块的子块"""
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


def create_callout_block(color: int = 2, emoji: str = "bulb") -> Dict[str, Any]:
    """
    创建空的高亮块（不包含文字）
    
    Args:
        color: 颜色编号 (0-7)
        emoji: 图标
    
    Returns:
        高亮块字典
    """
    return {
        "block_type": 19,  # 高亮块
        "callout": {
            "emoji_id": emoji,
            "background_color": color,
            "border_color": color
        }
    }





def add_callout_with_text(
    document_id: str,
    content: str,
    color: int = 2,
    emoji: str = "bulb",
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加高亮块并设置文本（分两步：创建 + 更新）
    
    Args:
        document_id: 文档 ID
        content: 高亮块内的文字内容
        color: 颜色编号 (0-7)
        emoji: 图标
    
    Returns:
        包含 block_id 的结果
    """
    # 步骤 1: 创建空的高亮块
    print("\n📌 步骤 1: 创建空的高亮块...")
    callout = create_callout_block(color=color, emoji=emoji)
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[callout],
        app_id=app_id,
        app_secret=app_secret
    )
    
    # 从 children 数组中获取 block_id
    children = result.get("children", [])
    if not children:
        raise Exception(f"创建高亮块失败，未返回 children，返回结果: {result}")
    
    callout_block_id = children[0].get("block_id")
    if not callout_block_id:
        raise Exception(f"创建高亮块失败，children 中没有 block_id，返回结果: {result}")
    
    print(f"✅ 高亮块创建成功，ID: {callout_block_id}")
    
    # 步骤 2: 获取高亮块的子块（空文本块）
    print(f"\n📌 步骤 2: 获取高亮块的子块...")
    children_data = get_block_children(document_id, callout_block_id, app_id, app_secret)
    child_blocks = children_data.get("items", [])
    
    if not child_blocks:
        raise Exception(f"高亮块没有子块")
    
    # 获取第一个子块（空文本块）的 ID
    child_block_id = child_blocks[0].get("block_id")
    print(f"✅ 获取到子块 ID: {child_block_id}")
    
    # 步骤 3: 更新子块的内容
    print(f"\n📌 步骤 3: 更新子块内容...")
    update_block_text(
        document_id=document_id,
        block_id=child_block_id,
        content=content,
        app_id=app_id,
        app_secret=app_secret
    )
    print(f"✅ 文本更新成功: {content}")
    
    return {
        "callout_block_id": callout_block_id,
        "child_block_id": child_block_id,
        "content": content
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档高亮块添加工具")
    print("=" * 60)
    
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")
    
    # 颜色编号对照
    colors = {
        "blue": 2,
        "gray": 1,
        "orange": 3,
        "yellow": 4,
        "green": 5,
        "red": 6,
        "purple": 7
    }
    
    try:
        # 添加一个高亮块并设置文本
        result = add_callout_with_text(
            document_id=document_id,
            content="高亮块测试",
            color=colors["blue"],  # 蓝色
            emoji="bulb"
        )
        
        print(f"\n📋 结果:")
        print(f"   高亮块 ID: {result['callout_block_id']}")
        print(f"   子块 ID: {result['child_block_id']}")
        print(f"   内容: {result['content']}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看高亮块")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
