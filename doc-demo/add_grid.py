#!/usr/bin/env python3
"""
飞书文档分栏（Grid）添加工具
支持在分栏中插入图片和文字
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/descendant
"""

import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import uuid

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


def get_block_children(
    document_id: str,
    block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """获取块的子块列表"""
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


def delete_blocks(
    document_id: str,
    parent_block_id: str,
    start_index: int = 0,
    end_index: Optional[int] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    批量删除子块
    
    Args:
        document_id: 文档 ID
        parent_block_id: 父块 ID
        start_index: 开始删除的索引位置（从0开始）
        end_index: 结束删除的索引位置（不包含）
        app_id: 应用 ID
        app_secret: 应用密钥
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{parent_block_id}/children/batch_delete"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    body = {
        "start_index": start_index
    }
    if end_index is not None:
        body["end_index"] = end_index
    
    resp = requests.delete(url, headers=headers, json=body)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"删除块失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def update_image_block(
    document_id: str,
    image_block_id: str,
    file_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """更新图片块，设置图片 token"""
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


def upload_image_to_block(
    file_path: str,
    image_block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """上传图片到指定的图片块"""
    from upload_file import upload_media
    
    return upload_media(
        file_path=file_path,
        parent_node=image_block_id,
        parent_type="docx_image",
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


def add_grid_with_content(
    document_id: str,
    image_path: Optional[str] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建 2x2 分栏，并在分栏中插入图片和文字
    
    根据飞书官方文档，使用两步法：
    1. 先创建 Grid block（系统会自动创建 Grid Column 和默认空白块）
    2. 获取 Grid Column ID，删除默认空白块，然后添加内容
    
    布局：
    - 左栏：图片
    - 右栏：文字说明
    """
    
    # 步骤 1: 创建 Grid block（2列分栏）
    print(f"\n📌 步骤 1: 创建 2 列分栏...")
    
    grid_block = {
        "block_type": 24,  # Grid 块
        "grid": {
            "column_size": 2  # 2 列分栏
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
    
    actual_grid_id = children[0].get("block_id")
    grid_children = children[0].get("children", [])
    
    if len(grid_children) < 2:
        raise Exception(f"分栏列数量不足，期望 2，实际 {len(grid_children)}")
    
    col1_id = grid_children[0]  # 第一列
    col2_id = grid_children[1]  # 第二列
    
    print(f"✅ 分栏创建成功，ID: {actual_grid_id}")
    print(f"   第一列 ID: {col1_id}")
    print(f"   第二列 ID: {col2_id}")
    
    # 步骤 2: 在第一列添加图片块
    print(f"\n📌 步骤 2: 在第一列添加图片...")
    
    image_block = {
        "block_type": 27,  # 图片块
        "image": {}  # 空图片块
    }
    
    result1 = add_blocks_to_document(
        document_id=document_id,
        blocks=[image_block],
        block_id=col1_id,
        app_id=app_id,
        app_secret=app_secret
    )
    
    col1_children = result1.get("children", [])
    if not col1_children:
        raise Exception("创建图片块失败")
    
    actual_image_id = col1_children[0].get("block_id")
    print(f"✅ 图片块创建成功，ID: {actual_image_id}")
    
    # 步骤 3: 在第二列添加文本
    print(f"\n📌 步骤 3: 在第二列添加文本...")
    
    text_blocks = [
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "图片说明",
                            "text_element_style": {
                                "bold": True,
                                "text_color": 5
                            }
                        }
                    }
                ],
                "style": {"align": 1}
            }
        },
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "这是左侧图片的详细说明。分栏布局可以很好地组织图文混排内容。",
                            "text_element_style": {}
                        }
                    }
                ],
                "style": {"align": 1}
            }
        },
        {
            "block_type": 2,
            "text": {
                "elements": [
                    {
                        "text_run": {
                            "content": "支持粗体、斜体、下划线等多种文本样式。",
                            "text_element_style": {
                                "italic": True,
                                "text_color": 7
                            }
                        }
                    }
                ],
                "style": {"align": 1}
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
    
    print(f"✅ 文本块添加成功")
    
    # 步骤 4: 上传图片（如果提供了图片路径）
    file_token = None
    if image_path and os.path.exists(image_path):
        print(f"\n📌 步骤 4: 上传图片...")
        file_token = upload_image_to_block(
            file_path=image_path,
            image_block_id=actual_image_id,
            app_id=app_id,
            app_secret=app_secret
        )
        
        print(f"\n📌 步骤 5: 更新图片块...")
        update_image_block(
            document_id=document_id,
            image_block_id=actual_image_id,
            file_token=file_token,
            app_id=app_id,
            app_secret=app_secret
        )
    
    return {
        "grid_block_id": actual_grid_id,
        "image_block_id": actual_image_id,
        "file_token": file_token
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档分栏添加工具")
    print("=" * 60)
    
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    image_path = "img.png"  # 本地图片路径
    
    print(f"\n📝 文档 ID: {document_id}")
    print(f"🖼️  图片路径: {image_path}")
    
    try:
        result = add_grid_with_content(
            document_id=document_id,
            image_path=image_path if os.path.exists(image_path) else None
        )
        
        print(f"\n📋 结果:")
        print(f"   分栏块 ID: {result['grid_block_id']}")
        print(f"   图片块 ID: {result['image_block_id']}")
        if result['file_token']:
            print(f"   图片 Token: {result['file_token']}")
        
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
