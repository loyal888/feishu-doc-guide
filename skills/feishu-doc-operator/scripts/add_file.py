#!/usr/bin/env python3
"""
飞书文档文件添加工具
支持上传本地文件到文档（PDF、Word、Excel等）
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
     POST /open-apis/drive/v1/medias/upload_all
     PATCH /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}

官方文档: https://open.feishu.cn/document/ukTMukTMukTM/uUDN04SN0QjL1QDN/document-docx/docx-v1/faq
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
from upload_file import upload_media, get_tenant_access_token


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


def update_file_block(
    document_id: str,
    file_block_id: str,
    file_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    更新文件块，设置文件 token

    使用 replace_file 操作
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET

    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")

    token = get_tenant_access_token(app_id, app_secret)

    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{file_block_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 使用 replace_file 操作设置文件 token
    body = {
        "replace_file": {
            "token": file_token
        }
    }

    resp = requests.patch(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"更新文件块失败 [{error_code}]: {error_msg}")

    print(f"   ✅ 文件块更新成功")
    return result.get("data", {})


def create_file_block() -> Dict[str, Any]:
    """
    创建文件块（会自动创建默认的视图块）

    Returns:
        文件块字典
    """
    return {
        "block_type": 23,  # 文件块
        "file": {
            "token": ""  # 空 token，后续更新
        }
    }


def add_file(
    document_id: str,
    file_path: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加文件到文档

    步骤（根据官方文档）：
    1. 创建文件块 → 返回视图块，视图块的 children 包含文件块 ID
    2. 上传文件，使用文件块 ID 作为 parent_node
    3. 使用 replace_file 操作更新文件块，设置文件 token

    Args:
        document_id: 文档 ID
        file_path: 本地文件路径
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        包含 block_id 和 file_token 的结果
    """
    print(f"\n📌 添加文件: {os.path.basename(file_path)}")

    # 步骤 1: 创建文件块
    print("   步骤 1: 创建文件块...")
    file_block = create_file_block()
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[file_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("创建文件块失败")

    # 创建文件块后，API 返回的是视图块（View Block）
    view_block_id = children[0].get("block_id")
    # 视图块的 children 包含文件块 ID
    file_block_children = children[0].get("children", [])
    if not file_block_children:
        raise Exception("视图块没有子块（文件块）")

    file_block_id = file_block_children[0]
    print(f"   ✅ 视图块 ID: {view_block_id}")
    print(f"   ✅ 文件块 ID: {file_block_id}")

    # 步骤 2: 上传文件，使用文件块 ID 作为 parent_node
    print("   步骤 2: 上传文件...")
    file_token = upload_media(
        file_path=file_path,
        parent_node=file_block_id,  # 使用文件块 ID！
        parent_type="docx_file",
        app_id=app_id,
        app_secret=app_secret
    )
    print(f"   ✅ 文件上传成功，token: {file_token}")

    # 步骤 3: 更新文件块，设置文件 token
    print("   步骤 3: 更新文件块...")
    update_file_block(
        document_id=document_id,
        file_block_id=file_block_id,
        file_token=file_token,
        app_id=app_id,
        app_secret=app_secret
    )

    print(f"✅ 文件添加完成")

    return {
        "view_block_id": view_block_id,
        "file_block_id": file_block_id,
        "file_token": file_token,
        "file_path": file_path
    }


def add_file_demo(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加文件示例

    演示插入本地文件
    """
    print("\n📌 创建文件...")

    # 检查文件是否存在（使用常见文件名作为示例）
    test_files = ["document.pdf", "example.docx", "data.xlsx", "file.txt"]
    file_path = None

    for f in test_files:
        if os.path.exists(f):
            file_path = f
            break

    if not file_path:
        print(f"   ⚠️ 未找到示例文件（尝试了: {', '.join(test_files)}），跳过文件演示")
        return {"block_ids": [], "count": 0}

    result = add_file(
        document_id=document_id,
        file_path=file_path,
        app_id=app_id,
        app_secret=app_secret
    )

    return {
        "block_ids": [result["view_block_id"]],
        "count": 1
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档文件添加工具")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 演示：添加文件
        print("\n" + "-" * 40)
        print("演示：添加本地文件")
        print("-" * 40)
        result = add_file_demo(
            document_id=document_id
        )
        print(f"   添加了 {result['count']} 个文件")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看文件")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
