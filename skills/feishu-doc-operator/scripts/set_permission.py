#!/usr/bin/env python3
"""
设置飞书文档权限 - 所有人可编辑
API: PATCH /open-apis/drive/v1/permissions/{token}/public
文档: https://open.feishu.cn/document/server-docs/docs/drive/permission/public
"""

import os
import requests
from typing import Optional, Dict, Any
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


def set_document_permission(
    document_id: str,
    link_share_entity: str = "anyone_editable",
    external_access: bool = True,
    security_entity: str = "anyone_can_edit",
    comment_entity: str = "anyone_can_edit",
    share_entity: str = "anyone",
    invite_external: bool = True,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    设置文档公开权限
    
    Args:
        document_id: 文档 ID (docx 文档的 token)
        link_share_entity: 链接分享设置
            - "closed": 关闭链接分享
            - "tenant_readable": 组织内可阅读
            - "tenant_editable": 组织内可编辑
            - "anyone_readable": 互联网上任何人可阅读
            - "anyone_editable": 互联网上任何人可编辑
        external_access: 允许内容被分享到组织外
        security_entity: 谁可以复制/下载/打印
        comment_entity: 谁可以评论
        share_entity: 谁可以添加协作者
        invite_external: 允许非管理员分享到组织外
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        权限设置结果
    """
    app_id = app_id or APP_ID
    app_secret = app_secret or APP_SECRET
    
    if not app_id or not app_secret:
        raise ValueError("缺少 APP_ID 或 APP_SECRET")
    
    token = get_tenant_access_token(app_id, app_secret)
    
    # 构建请求 URL
    url = f"{BASE_URL}/drive/v1/permissions/{document_id}/public"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Query 参数
    params = {
        "type": "docx"  # 新版文档类型
    }
    
    # Body 参数
    body = {
        "external_access": external_access,
        "security_entity": security_entity,
        "comment_entity": comment_entity,
        "share_entity": share_entity,
        "link_share_entity": link_share_entity,
        "invite_external": invite_external
    }
    
    resp = requests.patch(url, headers=headers, params=params, json=body)
    result = resp.json()
    
    if result.get("code") != 0:
        error_msg = result.get("msg", "未知错误")
        error_code = result.get("code")
        raise Exception(f"设置权限失败 [{error_code}]: {error_msg}")
    
    return result.get("data", {})


def set_anyone_can_edit(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    设置文档为所有人可编辑（简化函数）
    
    Args:
        document_id: 文档 ID
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        权限设置结果
    """
    return set_document_permission(
        document_id=document_id,
        link_share_entity="anyone_editable",  # 互联网上任何人可编辑
        external_access=True,
        security_entity="anyone_can_edit",
        comment_entity="anyone_can_edit",
        share_entity="anyone",
        invite_external=True,
        app_id=app_id,
        app_secret=app_secret
    )


def set_anyone_can_view(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    设置文档为所有人可查看（简化函数）
    
    Args:
        document_id: 文档 ID
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        权限设置结果
    """
    return set_document_permission(
        document_id=document_id,
        link_share_entity="anyone_readable",  # 互联网上任何人可阅读
        external_access=True,
        security_entity="anyone_can_view",
        comment_entity="anyone_can_view",
        share_entity="anyone",
        invite_external=True,
        app_id=app_id,
        app_secret=app_secret
    )


def main():
    """主函数 - 示例用法"""
    print("=" * 60)
    print("飞书文档权限设置工具")
    print("=" * 60)
    
    # 文档信息
    doc_url = "https://w6cz3sxm8a.feishu.cn/docx/SZPFdznFzo45B8xSYJpcexc2nje"
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    
    print(f"\n📝 文档链接: {doc_url}")
    print(f"📝 文档 ID: {document_id}")
    
    try:
        # 设置为所有人可编辑
        print("\n🔓 设置权限: 所有人可编辑...")
        result = set_anyone_can_edit(document_id)
        
        permission = result.get("permission_public", {})
        print(f"✅ 权限设置成功!")
        print(f"   链接分享: {permission.get('link_share_entity')}")
        print(f"   外部访问: {permission.get('external_access')}")
        print(f"   安全权限: {permission.get('security_entity')}")
        print(f"   评论权限: {permission.get('comment_entity')}")
        
        print("\n📋 权限说明:")
        print("   - 任何人获得链接后都可以编辑文档")
        print("   - 允许内容被分享到组织外")
        print("   - 任何人都可以复制、下载、打印")
        print("   - 任何人都可以添加协作者")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return 1
    
    print("\n" + "=" * 60)
    print("完成! 现在任何人都可以通过链接编辑此文档")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
