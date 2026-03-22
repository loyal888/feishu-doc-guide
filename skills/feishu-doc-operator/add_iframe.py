#!/usr/bin/env python3
"""
飞书文档内嵌块（Iframe）添加工具
支持嵌入哔哩哔哩、优酷、Figma、百度地图等第三方网页
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
"""

import os
import requests
import urllib.parse
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


def create_iframe_block(
    url: str,
    component_type: str = "bilibili"
) -> Dict[str, Any]:
    """
    创建内嵌块（Iframe）

    Args:
        url: 要嵌入的网页 URL（需要 URL Encode）
        component_type: 组件类型，可选值：
            - bilibili: 哔哩哔哩
            - youku: 优酷
            - figma: Figma
            - baidu_map: 百度地图
            - amap: 高德地图
            - xigua: 西瓜视频
            - airtable: Airtable
            - canva: Canva
            - codepen: CodePen
            - feishu_survey: 飞书问卷
            - jinshuju: 金数据

    Returns:
        内嵌块字典
    """
    # 组件类型映射
    type_mapping = {
        "bilibili": 1,
        "xigua": 2,
        "youku": 3,
        "airtable": 4,
        "baidu_map": 5,
        "amap": 6,
        "figma": 8,
        "modao": 9,
        "canva": 10,
        "codepen": 11,
        "feishu_survey": 12,
        "jinshuju": 13,
    }

    component_type_id = type_mapping.get(component_type, 1)

    # URL 需要编码
    encoded_url = urllib.parse.quote(url, safe='')

    return {
        "block_type": 26,  # Iframe 块
        "iframe": {
            "component": {
                "type": component_type_id,
                "url": encoded_url
            }
        }
    }


def add_iframe_demo(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加内嵌块示例

    演示 B站和 Figma 嵌入
    """
    print("\n📌 创建内嵌块...")

    blocks = []

    # 1. 哔哩哔哩视频
    print("   添加哔哩哔哩视频...")
    blocks.append(create_iframe_block(
        url="https://www.bilibili.com/video/BV1GJ411x7h7",
        component_type="bilibili"
    ))

    # 2. Figma 设计稿
    print("   添加 Figma 设计稿...")
    blocks.append(create_iframe_block(
        url="https://www.figma.com/file/xxxxx",
        component_type="figma"
    ))

    # 批量添加所有内嵌块
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=blocks,
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    block_ids = [child.get("block_id") for child in children]

    print(f"✅ 成功添加 {len(block_ids)} 个内嵌块")

    return {
        "block_ids": block_ids,
        "count": len(block_ids)
    }


def add_single_iframe(
    document_id: str,
    url: str,
    component_type: str = "bilibili",
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加单个内嵌块
    
    Args:
        document_id: 文档 ID
        url: 要嵌入的网页 URL
        component_type: 组件类型
        app_id: 应用 ID
        app_secret: 应用密钥
    
    Returns:
        包含 block_id 的结果
    """
    print(f"\n📌 添加 {component_type} 内嵌块...")
    print(f"   URL: {url}")
    
    iframe_block = create_iframe_block(url, component_type)
    
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[iframe_block],
        app_id=app_id,
        app_secret=app_secret
    )
    
    children = result.get("children", [])
    if not children:
        raise Exception("创建内嵌块失败")
    
    block_id = children[0].get("block_id")
    print(f"✅ 内嵌块创建成功，ID: {block_id}")
    
    return {
        "block_id": block_id,
        "url": url,
        "component_type": component_type
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档内嵌块添加工具")
    print("=" * 60)
    
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")
    
    try:
        # 演示1：批量添加各种内嵌块
        print("\n" + "-" * 40)
        print("演示1：批量添加内嵌块")
        print("-" * 40)
        result1 = add_iframe_demo(
            document_id=document_id
        )
        print(f"   添加了 {result1['count']} 个内嵌块")
        
        # 演示2：添加单个内嵌块（哔哩哔哩）
        print("\n" + "-" * 40)
        print("演示2：添加单个哔哩哔哩视频")
        print("-" * 40)
        result2 = add_single_iframe(
            document_id=document_id,
            url="https://www.bilibili.com/video/BV1xx411c7mD",
            component_type="bilibili"
        )
        print(f"   内嵌块 ID: {result2['block_id']}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看内嵌内容")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
