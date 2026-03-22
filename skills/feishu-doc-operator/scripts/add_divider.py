#!/usr/bin/env python3
"""
飞书文档分割线添加工具
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
"""

import os
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


def create_divider_block() -> Dict[str, Any]:
    """
    创建分割线块
    
    block_type: 22 - 分割线
    
    Returns:
        分割线块字典
    """
    return {
        "block_type": 22,  # 分割线块
        "divider": {}  # 分割线块是空结构体
    }


def add_dividers(
    document_id: str,
    count: int = 1,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加分割线到文档
    
    Args:
        document_id: 文档 ID
        count: 分割线数量
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        包含 block_ids 的结果
    """
    print(f"\n📌 添加 {count} 条分割线...")
    
    # 创建分割线块列表
    blocks = [create_divider_block() for _ in range(count)]
    
    # 批量添加分割线
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=blocks,
        app_id=app_id,
        app_secret=app_secret
    )
    
    children = result.get("children", [])
    block_ids = [child.get("block_id") for child in children]
    
    print(f"✅ 成功添加 {len(block_ids)} 条分割线")
    
    return {
        "block_ids": block_ids,
        "count": len(block_ids)
    }


def add_divider_with_text_demo(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加分割线示例（配合文本展示效果）
    """
    print("\n📌 创建分割线示例...")
    
    # 导入文本块创建函数（从 add_text.py）
    from add_text import create_text_element, create_text_block
    
    blocks = []
    
    # 添加标题文本
    blocks.append(create_text_block([
        create_text_element("第一部分", bold=True, text_color=5)
    ]))
    
    # 添加内容
    blocks.append(create_text_block([
        create_text_element("这是第一部分的内容，分割线用于区分文档的不同章节。")
    ]))
    
    # 添加分割线
    blocks.append(create_divider_block())
    
    # 添加第二部分标题
    blocks.append(create_text_block([
        create_text_element("第二部分", bold=True, text_color=4)
    ]))
    
    # 添加内容
    blocks.append(create_text_block([
        create_text_element("这是第二部分的内容，分割线让文档结构更清晰。")
    ]))
    
    # 添加分割线
    blocks.append(create_divider_block())
    
    # 添加第三部分标题
    blocks.append(create_text_block([
        create_text_element("第三部分", bold=True, text_color=6)
    ]))
    
    # 添加内容
    blocks.append(create_text_block([
        create_text_element("这是第三部分的内容，分割线是很好的视觉分隔符。")
    ]))
    
    # 批量添加所有块
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=blocks,
        app_id=app_id,
        app_secret=app_secret
    )
    
    children = result.get("children", [])
    block_ids = [child.get("block_id") for child in children]
    
    print(f"✅ 成功添加 {len(block_ids)} 个块（包含文本和分割线）")
    
    return {
        "block_ids": block_ids,
        "count": len(block_ids)
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档分割线添加工具")
    print("=" * 60)
    
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")
    
    try:
        # 演示1：单独添加分割线
        print("\n" + "-" * 40)
        print("演示1：单独添加分割线")
        print("-" * 40)
        result1 = add_dividers(
            document_id=document_id,
            count=3
        )
        print(f"   添加了 {result1['count']} 条分割线")
        
        # 演示2：分割线配合文本
        print("\n" + "-" * 40)
        print("演示2：分割线配合文本")
        print("-" * 40)
        result2 = add_divider_with_text_demo(
            document_id=document_id
        )
        print(f"   添加了 {result2['count']} 个块")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看分割线")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
