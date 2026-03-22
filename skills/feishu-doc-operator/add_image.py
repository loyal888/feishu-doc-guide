#!/usr/bin/env python3
"""
飞书文档图片添加工具
支持上传本地图片到文档
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
     POST /open-apis/drive/v1/medias/upload_all
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


def add_image(
    document_id: str,
    image_path: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加图片到文档

    步骤：
    1. 创建空图片块
    2. 上传图片到该块
    3. 更新图片块设置图片 token

    Args:
        document_id: 文档 ID
        image_path: 本地图片路径
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        包含 block_id 和 file_token 的结果
    """
    print(f"\n📌 添加图片: {os.path.basename(image_path)}")

    # 步骤 1: 创建空图片块
    print("   步骤 1: 创建空图片块...")
    image_block = create_empty_image_block()
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[image_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("创建图片块失败")

    image_block_id = children[0].get("block_id")
    print(f"   ✅ 图片块创建成功，ID: {image_block_id}")

    # 步骤 2: 上传图片
    print("   步骤 2: 上传图片...")
    file_token = upload_image_to_block(
        file_path=image_path,
        image_block_id=image_block_id,
        app_id=app_id,
        app_secret=app_secret
    )
    print(f"   ✅ 图片上传成功，token: {file_token}")

    # 步骤 3: 更新图片块
    print("   步骤 3: 更新图片块...")
    update_image_block(
        document_id=document_id,
        image_block_id=image_block_id,
        file_token=file_token,
        app_id=app_id,
        app_secret=app_secret
    )

    print(f"✅ 图片添加完成")

    return {
        "block_id": image_block_id,
        "file_token": file_token,
        "image_path": image_path
    }


def add_image_demo(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加图片示例

    演示插入本地图片 img.png
    """
    print("\n📌 创建图片...")

    # 检查图片文件是否存在
    image_path = "img.png"
    if not os.path.exists(image_path):
        print(f"   ⚠️ 图片文件 {image_path} 不存在，跳过图片演示")
        return {"block_ids": [], "count": 0}

    result = add_image(
        document_id=document_id,
        image_path=image_path,
        app_id=app_id,
        app_secret=app_secret
    )

    return {
        "block_ids": [result["block_id"]],
        "count": 1
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档图片添加工具")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 演示：添加图片
        print("\n" + "-" * 40)
        print("演示：添加本地图片")
        print("-" * 40)
        result = add_image_demo(
            document_id=document_id
        )
        print(f"   添加了 {result['count']} 张图片")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看图片")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
