#!/usr/bin/env python3
"""
飞书文档单元格（TableCell）操作工具
支持在表格单元格中插入文本、图片、列表等内容
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


def update_block_text(
    document_id: str,
    block_id: str,
    content: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """更新块文本内容"""
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    if not _app_id or not _app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "update_text_elements": {
            "elements": [
                {
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
        raise Exception(f"更新文本失败 [{error_code}]: {error_msg}")

    return result.get("data", {})


def create_table_block(
    rows: int,
    cols: int,
    column_width: Optional[List[int]] = None
) -> Dict[str, Any]:
    """创建表格块"""
    if column_width is None:
        column_width = [100] * cols

    return {
        "block_type": 31,
        "table": {
            "property": {
                "row_size": rows,
                "column_size": cols,
                "column_width": column_width
            }
        }
    }


def add_table_with_cell_content(
    document_id: str,
    rows: int = 2,
    cols: int = 2,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建表格并在单元格中插入各种内容

    演示内容：
    - 单元格 [0,0]: 普通文本
    - 单元格 [0,1]: 粗体文本
    - 单元格 [1,0]: 列表
    - 单元格 [1,1]: 图片（如果存在 img.png）
    """
    print(f"\n📌 创建 {rows}x{cols} 表格并填充单元格内容...")

    # 步骤 1: 创建表格
    print("   步骤 1: 创建表格...")
    table_block = create_table_block(rows, cols)
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[table_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("创建表格失败")

    table_block_id = children[0].get("block_id")
    print(f"   ✅ 表格创建成功，ID: {table_block_id}")

    # 步骤 2: 获取单元格
    print("   步骤 2: 获取单元格...")
    children_data = get_block_children(document_id, table_block_id, app_id, app_secret)
    cell_blocks = children_data.get("items", [])

    if len(cell_blocks) < rows * cols:
        raise Exception(f"单元格数量不足，期望 {rows * cols}，实际 {len(cell_blocks)}")

    print(f"   ✅ 获取到 {len(cell_blocks)} 个单元格")

    # 步骤 3: 向单元格插入内容
    print("   步骤 3: 向单元格插入内容...")

    # 单元格 [0,0]: 普通文本
    cell_00_id = cell_blocks[0].get("block_id")
    cell_children = get_block_children(document_id, cell_00_id, app_id, app_secret)
    text_blocks = cell_children.get("items", [])
    if text_blocks:
        update_block_text(document_id, text_blocks[0].get("block_id"), "普通文本", app_id, app_secret)
        print("   ✅ 单元格 [0,0]: 普通文本")

    # 单元格 [0,1]: 粗体文本
    cell_01_id = cell_blocks[1].get("block_id")
    cell_children = get_block_children(document_id, cell_01_id, app_id, app_secret)
    text_blocks = cell_children.get("items", [])
    if text_blocks:
        # 创建带样式的文本块
        _app_id = app_id or APP_ID
        _app_secret = app_secret or APP_SECRET
        token = get_tenant_access_token(_app_id, _app_secret)
        url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{text_blocks[0].get('block_id')}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        body = {
            "update_text_elements": {
                "elements": [
                    {
                        "text_run": {
                            "content": "粗体文本",
                            "text_element_style": {
                                "bold": True
                            }
                        }
                    }
                ]
            }
        }
        resp = requests.patch(url, headers=headers, json=body)
        if resp.json().get("code") == 0:
            print("   ✅ 单元格 [0,1]: 粗体文本")

    # 单元格 [1,0]: 无序列表
    cell_10_id = cell_blocks[2].get("block_id")
    list_block = {
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
    }
    add_blocks_to_document(document_id, [list_block], cell_10_id, app_id=app_id, app_secret=app_secret)
    print("   ✅ 单元格 [1,0]: 无序列表")

    # 单元格 [1,1]: 图片（如果存在）
    cell_11_id = cell_blocks[3].get("block_id")
    if os.path.exists("img.png"):
        # 创建图片块
        image_block = {"block_type": 27, "image": {}}
        result = add_blocks_to_document(document_id, [image_block], cell_11_id, app_id=app_id, app_secret=app_secret)
        image_children = result.get("children", [])
        if image_children:
            image_block_id = image_children[0].get("block_id")
            # 上传图片
            _app_id = app_id or APP_ID
            _app_secret = app_secret or APP_SECRET
            file_token = upload_image_to_block("img.png", image_block_id, _app_id, _app_secret)
            # 更新图片块
            token = get_tenant_access_token(_app_id, _app_secret)
            url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{image_block_id}"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            body = {"replace_image": {"token": file_token}}
            requests.patch(url, headers=headers, json=body)
            print("   ✅ 单元格 [1,1]: 图片")
    else:
        # 插入文本
        cell_children = get_block_children(document_id, cell_11_id, app_id, app_secret)
        text_blocks = cell_children.get("items", [])
        if text_blocks:
            update_block_text(document_id, text_blocks[0].get("block_id"), "图片占位", app_id, app_secret)
            print("   ✅ 单元格 [1,1]: 图片占位（img.png 不存在）")

    return {
        "table_block_id": table_block_id,
        "cell_blocks": cell_blocks,
        "rows": rows,
        "cols": cols
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档单元格操作工具")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 演示：创建表格并填充单元格
        print("\n" + "-" * 40)
        print("演示：表格单元格内容")
        print("-" * 40)
        result = add_table_with_cell_content(
            document_id=document_id,
            rows=2,
            cols=2
        )
        print(f"\n✅ 表格创建完成，ID: {result['table_block_id']}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看表格")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
