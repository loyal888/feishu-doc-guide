#!/usr/bin/env python3
"""
飞书文件上传模块
支持上传图片、文件等素材到云文档
API: POST /open-apis/drive/v1/medias/upload_all
"""

import os
import requests
from typing import Optional
from dotenv import load_dotenv
from requests_toolbelt import MultipartEncoder

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


def upload_media(
    file_path: str,
    parent_node: str,
    parent_type: str = "docx_image",
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """
    上传媒体文件到飞书
    
    Args:
        file_path: 本地文件路径
        parent_node: 上传点的 token（如图片块 ID、文档 ID 等）
        parent_type: 上传点类型，可选值：
            - docx_image: 新版文档图片
            - docx_file: 新版文档文件
            - doc_image: 旧版文档图片
            - doc_file: 旧版文档文件
            - sheet_image: 电子表格图片
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        file_token: 文件的唯一标识
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)
    
    url = f"{BASE_URL}/drive/v1/medias/upload_all"
    
    # 构建 multipart 表单
    with open(file_path, 'rb') as f:
        form = {
            'file_name': file_name,
            'parent_type': parent_type,
            'parent_node': parent_node,
            'size': str(file_size),
            'file': (file_name, f, 'application/octet-stream')
        }
        
        multi_form = MultipartEncoder(form)
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': multi_form.content_type
        }
        
        resp = requests.post(url, headers=headers, data=multi_form)
    
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"上传文件失败 [{error_code}]: {error_msg}")
    
    file_token = result.get("data", {}).get("file_token")
    print(f"✅ 文件上传成功，file_token: {file_token}")
    return file_token


def upload_image_to_block(
    file_path: str,
    image_block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """
    上传图片到指定的图片块
    
    Args:
        file_path: 本地图片路径
        image_block_id: 图片块 ID（parent_node）
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        file_token: 图片的唯一标识
    """
    return upload_media(
        file_path=file_path,
        parent_node=image_block_id,
        parent_type="docx_image",
        app_id=app_id,
        app_secret=app_secret
    )


def upload_file_to_block(
    file_path: str,
    file_block_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """
    上传文件到指定的文件块
    
    Args:
        file_path: 本地文件路径
        file_block_id: 文件块 ID（parent_node）
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        file_token: 文件的唯一标识
    """
    return upload_media(
        file_path=file_path,
        parent_node=file_block_id,
        parent_type="docx_file",
        app_id=app_id,
        app_secret=app_secret
    )


if __name__ == "__main__":
    # 测试代码
    print("=" * 60)
    print("飞书文件上传模块")
    print("=" * 60)
    
    # 检查环境变量
    if not APP_ID or not APP_SECRET:
        print("\n❌ 错误: 请设置 APP_ID 和 APP_SECRET 环境变量")
        exit(1)
    
    print(f"\n✅ 环境变量检查通过")
    print(f"   APP_ID: {APP_ID[:6]}...")
    
    # 测试获取 token
    try:
        token = get_tenant_access_token(APP_ID, APP_SECRET)
        print(f"   Token: {token[:20]}...")
        print("\n✅ 模块加载成功")
    except Exception as e:
        print(f"\n❌ 获取 token 失败: {e}")
        exit(1)
