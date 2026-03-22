#!/usr/bin/env python3
"""
飞书文档小组件（AddOns）Demo
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
     block_type: 35 (AddOns)
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

# 导入 token 获取函数
from upload_file import get_tenant_access_token


def add_blocks_to_document(
    document_id: str,
    blocks: List[Dict[str, Any]],
    block_id: Optional[str] = None,
    index: Optional[int] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """向文档添加块"""
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    if not _app_id or not _app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")

    token = get_tenant_access_token(_app_id, _app_secret)
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


def add_addon_to_document(
    document_id: str,
    addon_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """
    添加文档小组件到文档

    Args:
        document_id: 文档 ID
        addon_token: 小组件 token
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        小组件块 ID
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    # 创建 AddOns 块
    addon_block = {
        "block_type": 35,  # AddOns 块
        "add_ons": {
            "token": addon_token
        }
    }

    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[addon_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("添加小组件失败")

    block_id = children[0].get("block_id")
    print(f"   ✅ 小组件已添加到文档")
    print(f"   Block ID: {block_id}")
    return block_id


def add_text_block(
    document_id: str,
    text: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """添加文本块到文档"""
    text_block = {
        "block_type": 2,  # 文本块
        "text": {
            "elements": [
                {
                    "type": "text_run",
                    "text_run": {
                        "content": text
                    }
                }
            ]
        }
    }

    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[text_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if children:
        return children[0].get("block_id")
    return None


def demo_addon():
    """演示文档小组件功能"""
    print("=" * 60)
    print("飞书文档小组件（AddOns）Demo")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 添加说明文本
        print("\n📌 添加说明文本...")
        add_text_block(document_id, "📦 文档小组件示例：")
        print("   ✅ 说明文本已添加")

        # 尝试添加小组件
        # 注意：小组件需要预先在飞书开放平台创建并获取 token
        # 这里使用一个示例 token，实际使用时需要替换为真实的小组件 token
        print("\n📌 尝试添加文档小组件...")
        print("   ⚠️ 注意：需要先在飞书开放平台创建小组件并获取 token")
        
        # 示例小组件 token（需要替换为真实的）
        # addon_token = "your_addon_token_here"
        # add_addon_to_document(document_id, addon_token)
        
        print("\n   📋 小组件信息：")
        print("   - block_type: 35 (AddOns)")
        print("   - 需要参数: token (小组件标识)")
        print("   - 创建方式: 飞书开放平台 -> 应用 -> 小组件")
        
        # 添加更多说明
        print("\n📌 添加使用说明...")
        instructions = [
            "",
            "📝 使用说明：",
            "1. 访问飞书开放平台 (https://open.feishu.cn)",
            "2. 创建企业自建应用",
            "3. 在应用中添加小组件能力",
            "4. 获取小组件 token",
            "5. 使用 add_addon_to_document() 函数添加到文档",
            "",
            "⚠️ 注意：小组件需要特殊权限才能创建和使用"
        ]
        for line in instructions:
            add_text_block(document_id, line)
        print("   ✅ 使用说明已添加")

        print("\n✅ Demo 完成")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看内容")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(demo_addon())
