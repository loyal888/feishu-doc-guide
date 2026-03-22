#!/usr/bin/env python3
"""
获取画板节点数据结构
"""

import os
import requests
import json
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


def get_board_nodes(
    whiteboard_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    获取画板中的所有节点

    Args:
        whiteboard_id: 画板 ID
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        节点列表
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/board/v1/whiteboards/{whiteboard_id}/nodes"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers)
    result = resp.json()

    if result.get("code") == 0:
        nodes = result.get("data", {}).get("nodes", [])
        print(f"✅ 获取节点成功，共 {len(nodes)} 个节点")
        return nodes
    else:
        print(f"❌ 获取节点失败: {result.get('msg')}")
        return []


def main():
    """主函数"""
    # 使用用户提供的 whiteboard_id
    whiteboard_id = "NW1zwArewhEMFJbrtHkcXEIPnQb"
    
    print(f"📝 Whiteboard ID: {whiteboard_id}")
    print("\n📌 获取画板节点...")
    
    nodes = get_board_nodes(whiteboard_id)
    
    if not nodes:
        print("⚠️ 画板中没有节点")
        return
    
    print("\n" + "=" * 60)
    print("节点数据结构:")
    print("=" * 60)
    
    for i, node in enumerate(nodes, 1):
        print(f"\n--- 节点 {i} ---")
        print(f"ID: {node.get('id')}")
        print(f"Type: {node.get('type')}")
        
        # 打印完整节点结构
        print("\n完整结构:")
        print(json.dumps(node, indent=2, ensure_ascii=False))
        
        # 如果是 connector 类型，特别标注
        if node.get('type') == 'connector':
            print("\n🔌 这是一个连线节点！")
            if 'connector' in node:
                print("Connector 结构:")
                print(json.dumps(node['connector'], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
