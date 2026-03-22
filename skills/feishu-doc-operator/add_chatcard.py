#!/usr/bin/env python3
"""
飞书文档会话卡片（ChatCard）添加工具
支持在文档中嵌入群聊会话卡片
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


def create_chatcard_block(
    chat_id: str,
    align: int = 1
) -> Dict[str, Any]:
    """
    创建会话卡片块（ChatCard）

    Args:
        chat_id: 群聊会话 OpenID，以 'oc_' 开头
        align: 对齐方式，1=居左(默认), 2=居中, 3=居右

    Returns:
        会话卡片块字典
    """
    return {
        "block_type": 20,  # 会话卡片块
        "chat_card": {
            "chat_id": chat_id,
            "align": align
        }
    }


def add_chatcard_demo(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加会话卡片示例

    演示不同对齐方式的会话卡片
    """
    print("\n📌 创建会话卡片...")

    # 使用真实的群聊 OpenID
    chat_id = "oc_4c5631e61992ce219ab00431f60787d5"

    blocks = []

    # 1. 居左对齐的会话卡片
    print("   添加居左对齐的会话卡片...")
    blocks.append(create_chatcard_block(
        chat_id=chat_id,
        align=1  # 居左
    ))

    # 2. 居中对齐的会话卡片
    print("   添加居中对齐的会话卡片...")
    blocks.append(create_chatcard_block(
        chat_id=chat_id,
        align=2  # 居中
    ))

    # 批量添加所有会话卡片
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=blocks,
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    block_ids = [child.get("block_id") for child in children]

    print(f"✅ 成功添加 {len(block_ids)} 个会话卡片")

    return {
        "block_ids": block_ids,
        "count": len(block_ids)
    }


def add_single_chatcard(
    document_id: str,
    chat_id: str,
    align: int = 1,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加单个会话卡片

    Args:
        document_id: 文档 ID
        chat_id: 群聊会话 OpenID，以 'oc_' 开头
        align: 对齐方式，1=居左, 2=居中, 3=居右
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        包含 block_id 的结果
    """
    print(f"\n📌 添加会话卡片...")
    print(f"   Chat ID: {chat_id}")
    print(f"   对齐方式: {['', '居左', '居中', '居右'][align]}")

    chatcard_block = create_chatcard_block(chat_id, align)

    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[chatcard_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("创建会话卡片失败")

    block_id = children[0].get("block_id")
    print(f"✅ 会话卡片创建成功，ID: {block_id}")

    return {
        "block_id": block_id,
        "chat_id": chat_id,
        "align": align
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档会话卡片添加工具")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 演示1：批量添加会话卡片示例
        print("\n" + "-" * 40)
        print("演示1：批量添加会话卡片")
        print("-" * 40)
        result1 = add_chatcard_demo(
            document_id=document_id
        )
        print(f"   添加了 {result1['count']} 个会话卡片")

        # 演示2：添加单个会话卡片（需要替换为真实的 chat_id）
        print("\n" + "-" * 40)
        print("演示2：添加单个会话卡片")
        print("-" * 40)
        print("   注意：请将 example_chat_id 替换为真实的群聊 OpenID")
        # 取消下面的注释并替换为真实的 chat_id 来测试
        # result2 = add_single_chatcard(
        #     document_id=document_id,
        #     chat_id="oc_xxxxxxxxxxxxxxxxxxxxxxxxxx",  # 替换为真实的群聊 OpenID
        #     align=1
        # )
        # print(f"   会话卡片 ID: {result2['block_id']}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看会话卡片")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
