#!/usr/bin/env python3
"""
飞书文档分栏列（GridColumn）操作工具
支持在分栏列中插入文本、图片、列表等内容
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

# 导入文件上传模块
from upload_file import upload_image_to_block, get_tenant_access_token


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


def get_block_children(
    document_id: str,
    block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """获取块的子块"""
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    if not _app_id or not _app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")

    token = get_tenant_access_token(_app_id, _app_secret)

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


def update_image_block(
    document_id: str,
    image_block_id: str,
    file_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """更新图片块，设置图片 token"""
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    if not _app_id or not _app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{image_block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "replace_image": {
            "token": file_token
        }
    }

    resp = requests.patch(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"更新图片块失败 [{error_code}]: {error_msg}")

    print(f"   ✅ 图片块更新成功")
    return result.get("data", {})


def add_grid_with_columns(
    document_id: str,
    cols: int = 2,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建分栏并在分栏列中插入各种内容

    演示内容（2列分栏）：
    - 第一列: 图片
    - 第二列: 标题 + 描述文本 + 无序列表
    """
    print(f"\n📌 创建 {cols} 列分栏并填充内容...")

    # 步骤 1: 创建分栏（Grid）
    print("   步骤 1: 创建分栏...")
    grid_block = {
        "block_type": 24,  # Grid 块
        "grid": {
            "column_size": cols  # 列数
        }
    }
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[grid_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("创建分栏失败")

    grid_block_id = children[0].get("block_id")
    grid_children = children[0].get("children", [])

    if len(grid_children) < cols:
        raise Exception(f"分栏列数量不足，期望 {cols}，实际 {len(grid_children)}")

    print(f"   ✅ 分栏创建成功，ID: {grid_block_id}")
    print(f"   ✅ 获取到 {len(grid_children)} 个分栏列")

    # 步骤 2: 向分栏列插入内容
    print("   步骤 2: 向分栏列插入内容...")

    # 第一列：图片
    col1_id = grid_children[0]
    print(f"\n   📌 第一列（{col1_id}）: 添加图片...")
    image_block = {"block_type": 27, "image": {}}  # 图片块
    result1 = add_blocks_to_document(
        document_id=document_id,
        blocks=[image_block],
        block_id=col1_id,
        app_id=app_id,
        app_secret=app_secret
    )
    col1_children = result1.get("children", [])
    if col1_children:
        image_block_id = col1_children[0].get("block_id")
        if os.path.exists("img.png"):
            file_token = upload_image_to_block("img.png", image_block_id, app_id or APP_ID, app_secret or APP_SECRET)
            update_image_block(document_id, image_block_id, file_token, app_id, app_secret)
            print("   ✅ 第一列: 图片")
        else:
            print("   ✅ 第一列: 图片占位（img.png 不存在）")

    # 第二列：标题 + 描述 + 列表
    col2_id = grid_children[1]
    print(f"\n   📌 第二列（{col2_id}）: 添加文本...")
    text_blocks = [
        {
            "block_type": 3,  # 标题1
            "heading1": {
                "elements": [
                    {
                        "text_run": {
                            "content": "图片标题",
                            "text_element_style": {"bold": True}
                        }
                    }
                ]
            }
        },
        {
            "block_type": 2,  # 文本
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是左侧图片的详细说明。分栏布局可以很好地组织图文混排内容。",
                            "text_element_style": {}
                        }
                    }
                ]
            }
        },
        {
            "block_type": 12,  # 无序列表
            "bullet": {
                "elements": [
                    {
                        "text_run": {
                            "content": "列表项 1",
                            "text_element_style": {}
                        }
                    }
                ]
            }
        },
        {
            "block_type": 12,  # 无序列表
            "bullet": {
                "elements": [
                    {
                        "text_run": {
                            "content": "列表项 2",
                            "text_element_style": {}
                        }
                    }
                ]
            }
        }
    ]
    add_blocks_to_document(
        document_id=document_id,
        blocks=text_blocks,
        block_id=col2_id,
        app_id=app_id,
        app_secret=app_secret
    )
    print("   ✅ 第二列: 标题 + 描述 + 列表")

    return {
        "grid_block_id": grid_block_id,
        "column_ids": grid_children,
        "cols": cols
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档分栏列操作工具")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 演示：创建分栏并填充分栏列
        print("\n" + "-" * 40)
        print("演示：分栏列内容")
        print("-" * 40)
        result = add_grid_with_columns(
            document_id=document_id,
            cols=2
        )
        print(f"\n✅ 分栏创建完成，ID: {result['grid_block_id']}")
        print(f"   分栏列数量: {len(result['column_ids'])}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看分栏效果")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
