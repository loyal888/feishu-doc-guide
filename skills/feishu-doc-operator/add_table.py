#!/usr/bin/env python3
"""
向飞书文档添加表格，并向单元格内插入文字和图片
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
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

# 导入文件上传模块
from upload_file import upload_image_to_block, get_tenant_access_token


def upload_image(
    file_path: str,
    image_block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """
    上传图片到飞书（上传到指定的图片块）
    
    Args:
        file_path: 本地图片路径
        image_block_id: 图片块 ID（parent_node）
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        file_token
    """
    return upload_image_to_block(
        file_path=file_path,
        image_block_id=image_block_id,
        app_id=app_id,
        app_secret=app_secret
    )


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


def update_block_text(
    document_id: str,
    block_id: str,
    content: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """更新文本块内容"""
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


def create_empty_image_block() -> Dict[str, Any]:
    """
    创建空图片块（用于后续上传图片）
    
    Returns:
        图片块字典
    """
    return {
        "block_type": 27,  # 图片块
        "image": {}  # 空图片块，后续上传图片并更新
    }


def update_image_block(
    document_id: str,
    image_block_id: str,
    file_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    更新图片块，设置图片 token
    
    Args:
        document_id: 文档 ID
        image_block_id: 图片块 ID
        file_token: 图片的 file_token
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        更新结果
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{image_block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 使用 replace_image 操作设置图片 token
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
    
    print(f"✅ 图片块更新成功")
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


def add_table_with_content(
    document_id: str,
    rows: int,
    cols: int,
    cell_contents: List[List[str]],
    column_width: Optional[List[int]] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """添加表格并填充内容"""
    # 步骤 1: 创建表格
    print(f"\n📌 步骤 1: 创建 {rows}x{cols} 表格...")
    table_block = create_table_block(rows, cols, column_width)
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[table_block],
        app_id=app_id,
        app_secret=app_secret
    )
    
    # 获取表格块 ID
    children = result.get("children", [])
    if not children:
        raise Exception("创建表格失败")
    
    table_block_id = children[0].get("block_id")
    print(f"✅ 表格创建成功，ID: {table_block_id}")
    
    # 步骤 2: 获取表格的单元格子块
    print(f"\n📌 步骤 2: 获取表格单元格...")
    children_data = get_block_children(document_id, table_block_id, app_id, app_secret)
    cell_blocks = children_data.get("items", [])
    
    if len(cell_blocks) < rows * cols:
        raise Exception(f"单元格数量不足，期望 {rows * cols}，实际 {len(cell_blocks)}")
    
    print(f"✅ 获取到 {len(cell_blocks)} 个单元格")
    
    # 步骤 3: 向每个单元格内插入文字
    print(f"\n📌 步骤 3: 向单元格内插入文字...")
    for row_idx in range(rows):
        for col_idx in range(cols):
            cell_idx = row_idx * cols + col_idx
            cell_block = cell_blocks[cell_idx]
            cell_block_id = cell_block.get("block_id")
            
            # 获取单元格内容
            content = None
            if row_idx < len(cell_contents) and col_idx < len(cell_contents[row_idx]):
                content = cell_contents[row_idx][col_idx]
            
            # 如果内容为 None，跳过该单元格（用于后续插入图片等操作）
            if content is None:
                print(f"   ⏭️  单元格 [{row_idx},{col_idx}]: 跳过（预留）")
                continue
            
            # 获取单元格内的文本块
            cell_children_data = get_block_children(document_id, cell_block_id, app_id, app_secret)
            text_blocks = cell_children_data.get("items", [])
            
            if text_blocks:
                # 更新第一个文本块的内容
                text_block_id = text_blocks[0].get("block_id")
                update_block_text(
                    document_id=document_id,
                    block_id=text_block_id,
                    content=content,
                    app_id=app_id,
                    app_secret=app_secret
                )
                print(f"   ✅ 单元格 [{row_idx},{col_idx}]: {content}")
    
    return {
        "table_block_id": table_block_id,
        "cell_blocks": cell_blocks,
        "rows": rows,
        "cols": cols
    }


def create_nested_blocks(
    document_id: str,
    block_id: str,
    children_ids: List[str],
    descendants: List[Dict[str, Any]],
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建嵌套块（一次性创建完整的块结构）
    API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/descendant
    
    Args:
        document_id: 文档 ID
        block_id: 父块 ID
        children_ids: 子块 ID 列表（用于指定 descendants 中哪些块是直接的子块）
        descendants: 嵌套的块结构列表
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        创建结果
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{block_id}/descendant"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "children_id": children_ids,
        "descendants": descendants
    }
    
    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"创建嵌套块失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def add_table_with_image(
    document_id: str,
    image_path: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加表格并在单元格中插入图片
    
    使用创建嵌套块方式（descendant API）一次性创建完整的表格结构，
    避免默认文本块的问题
    """
    import uuid
    
    # 生成临时的 block_id（用于嵌套块创建）
    table_id = f"table_{uuid.uuid4().hex[:16]}"
    cell_00_id = f"cell00_{uuid.uuid4().hex[:16]}"  # 左上
    cell_01_id = f"cell01_{uuid.uuid4().hex[:16]}"  # 右上
    cell_10_id = f"cell10_{uuid.uuid4().hex[:16]}"  # 左下（图片）
    cell_11_id = f"cell11_{uuid.uuid4().hex[:16]}"  # 右下
    text_00_id = f"text00_{uuid.uuid4().hex[:16]}"
    text_01_id = f"text01_{uuid.uuid4().hex[:16]}"
    image_id = f"img_{uuid.uuid4().hex[:16]}"
    text_11_id = f"text11_{uuid.uuid4().hex[:16]}"
    
    # 步骤 1: 使用嵌套块 API 一次性创建带图片的表格
    print(f"\n📌 步骤 1: 创建带图片的表格（使用嵌套块）...")
    
    descendants = [
        # 表格块
        {
            "block_id": table_id,
            "block_type": 31,
            "table": {
                "property": {
                    "row_size": 2,
                    "column_size": 2,
                    "column_width": [200, 150]
                }
            },
            "children": [cell_00_id, cell_01_id, cell_10_id, cell_11_id]
        },
        # 单元格 00 - 文本
        {
            "block_id": cell_00_id,
            "block_type": 32,
            "table_cell": {},
            "children": [text_00_id]
        },
        {
            "block_id": text_00_id,
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "图片展示",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {"align": 1}
            }
        },
        # 单元格 01 - 文本
        {
            "block_id": cell_01_id,
            "block_type": 32,
            "table_cell": {},
            "children": [text_01_id]
        },
        {
            "block_id": text_01_id,
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "说明",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {"align": 1}
            }
        },
        # 单元格 10 - 图片（关键：直接创建图片块，没有默认文本块）
        {
            "block_id": cell_10_id,
            "block_type": 32,
            "table_cell": {},
            "children": [image_id]
        },
        {
            "block_id": image_id,
            "block_type": 27,
            "image": {}  # 空图片块，后续上传
        },
        # 单元格 11 - 文本
        {
            "block_id": cell_11_id,
            "block_type": 32,
            "table_cell": {},
            "children": [text_11_id]
        },
        {
            "block_id": text_11_id,
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是上传的图片",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {"align": 1}
            }
        }
    ]
    
    result = create_nested_blocks(
        document_id=document_id,
        block_id=document_id,  # 在文档根节点下创建
        children_ids=[table_id],  # 表格块是文档的直接子块
        descendants=descendants,
        app_id=app_id,
        app_secret=app_secret
    )
    
    # 从返回结果中获取实际的 block_id
    children = result.get("children", [])
    if not children:
        raise Exception("创建嵌套块失败，未返回 children")
    
    # 获取表格块的实际 ID
    actual_table_id = children[0].get("block_id")
    print(f"✅ 表格创建成功，ID: {actual_table_id}")
    
    # 获取表格的子块（单元格）
    table_children = children[0].get("children", [])
    if len(table_children) < 4:
        raise Exception(f"表格单元格数量不足，期望 4，实际 {len(table_children)}")
    
    # 左下角单元格是第 3 个（索引 2）
    target_cell_id = table_children[2]
    
    # 获取单元格的子块（应该是图片块）
    cell_children_data = get_block_children(document_id, target_cell_id, app_id, app_secret)
    cell_children = cell_children_data.get("items", [])
    if not cell_children:
        raise Exception("单元格内没有子块")
    
    actual_image_id = cell_children[0].get("block_id")
    print(f"✅ 图片块创建成功，ID: {actual_image_id}")
    
    # 步骤 2: 上传图片到该图片块
    print(f"\n📌 步骤 2: 上传图片...")
    file_token = upload_image(
        file_path=image_path,
        image_block_id=actual_image_id,
        app_id=app_id,
        app_secret=app_secret
    )
    
    # 步骤 3: 更新图片块，设置图片 token
    print(f"\n📌 步骤 3: 更新图片块...")
    update_image_block(
        document_id=document_id,
        image_block_id=actual_image_id,
        file_token=file_token,
        app_id=app_id,
        app_secret=app_secret
    )
    
    return {
        "table_block_id": actual_table_id,
        "image_block_id": actual_image_id,
        "file_token": file_token
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档表格添加工具（带图片）")
    print("=" * 60)
    
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")
    
    # 检查是否存在 img.png
    image_path = "img.png"
    if not os.path.exists(image_path):
        print(f"\n⚠️  {image_path} 不存在，请先准备图片文件")
        print("   将使用纯文本表格演示...")
        
        try:
            # 添加纯文本表格
            result = add_table_with_content(
                document_id=document_id,
                rows=2,
                cols=2,
                cell_contents=[
                    ["姓名", "年龄"],
                    ["张三", "25"]
                ],
                column_width=[150, 100]
            )
            print(f"\n📋 结果:")
            print(f"   表格 ID: {result['table_block_id']}")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            return 1
    else:
        try:
            # 添加带图片的表格
            result = add_table_with_image(
                document_id=document_id,
                image_path=image_path
            )
            print(f"\n📋 结果:")
            print(f"   表格 ID: {result['table_block_id']}")
            print(f"   图片块 ID: {result['image_block_id']}")
            print(f"   图片 Token: {result['file_token']}")
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
