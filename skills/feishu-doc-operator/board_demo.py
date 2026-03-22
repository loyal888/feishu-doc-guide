#!/usr/bin/env python3
"""
飞书画板（Board）Demo
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
     block_type: 43 (Board)
     GET /open-apis/board/v1/whiteboards/{whiteboard_id}/nodes
     POST /open-apis/board/v1/whiteboards/{whiteboard_id}/nodes
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

# 导入 token 获取函数
from upload_file import get_tenant_access_token


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


def add_board_to_document(
    document_id: str,
    title: str = "画板",
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加画板到文档

    Args:
        document_id: 文档 ID
        title: 画板标题
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        画板信息，包含 whiteboard_id
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    # 创建 Board 块
    board_block = {
        "block_type": 43,  # Board 块
        "board": {
            "title": title
        }
    }

    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[board_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("添加画板失败")

    block_info = children[0]
    block_id = block_info.get("block_id")
    whiteboard_id = block_info.get("board", {}).get("token", "")
    
    print(f"   ✅ 画板已添加到文档")
    print(f"   Block ID: {block_id}")
    print(f"   Whiteboard ID: {whiteboard_id}")
    
    return {
        "block_id": block_id,
        "whiteboard_id": whiteboard_id
    }


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
        print(f"   ✅ 获取节点成功，共 {len(nodes)} 个节点")
        return nodes
    else:
        print(f"   ❌ 获取节点失败: {result.get('msg')}")
        return []


def create_board_node(
    whiteboard_id: str,
    shape_type: str,
    x: float,
    y: float,
    width: float,
    height: float,
    text: str = "",
    parent_id: Optional[str] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Optional[str]:
    """
    在画板中创建节点

    Args:
        whiteboard_id: 画板 ID
        shape_type: 形状类型，如 "rect", "ellipse", "diamond" 等
        x: X 坐标
        y: Y 坐标
        width: 宽度
        height: 高度
        text: 文本内容
        parent_id: 父节点 ID（可选）
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        节点 ID
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/board/v1/whiteboards/{whiteboard_id}/nodes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 对于 rect, ellipse, diamond 等形状，需要使用 composite_shape 类型
    # 并在 composite_shape 中指定子类型
    node_data = {
        "type": "composite_shape",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "composite_shape": {
            "type": shape_type
        }
    }

    if text:
        node_data["text"] = {
            "text": text,
            "font_size": 14,
            "horizontal_align": "center",
            "vertical_align": "mid"
        }

    if parent_id:
        node_data["parent_id"] = parent_id

    # 根据飞书 API 文档，请求体应该是 nodes 数组
    body = {"nodes": [node_data]}

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        # API 返回的是 ids 数组
        ids = result.get("data", {}).get("ids", [])
        if ids:
            node_id = ids[0]
            print(f"   ✅ 节点创建成功: {node_id}")
            return node_id
        else:
            print(f"   ⚠️ 节点创建返回空 ids")
            return None
    else:
        print(f"   ❌ 节点创建失败: {result.get('msg')}")
        return None


def create_connector(
    whiteboard_id: str,
    start_node_id: str,
    end_node_id: str,
    shape: str = "straight",
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Optional[str]:
    """
    在画板中创建连线

    Args:
        whiteboard_id: 画板 ID
        start_node_id: 起始节点 ID
        end_node_id: 结束节点 ID
        shape: 连线形状，如 "straight"(直线), "polyline"(折线), "curve"(曲线)
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        连线节点 ID
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/board/v1/whiteboards/{whiteboard_id}/nodes"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 连线使用 connector 类型
    # 根据实际数据结构，position 是包含 x, y 的对象
    node_data = {
        "type": "connector",
        "x": 0,
        "y": 0,
        "width": 100,
        "height": 100,
        "connector": {
            "start": {
                "arrow_style": "none",
                "attached_object": {
                    "id": start_node_id,
                    "position": {
                        "x": 1,
                        "y": 0.5
                    },
                    "snap_to": "right"
                }
            },
            "end": {
                "arrow_style": "line_arrow",
                "attached_object": {
                    "id": end_node_id,
                    "position": {
                        "x": 0,
                        "y": 0.5
                    },
                    "snap_to": "left"
                }
            },
            "shape": shape,
            "specified_coordinate": True,
            "caption_auto_direction": False,
            "turning_points": []
        }
    }

    body = {"nodes": [node_data]}

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        ids = result.get("data", {}).get("ids", [])
        if ids:
            node_id = ids[0]
            print(f"   ✅ 连线创建成功: {node_id}")
            return node_id
        else:
            print(f"   ⚠️ 连线创建返回空 ids")
            return None
    else:
        print(f"   ❌ 连线创建失败: {result.get('msg')}")
        return None


def add_text_block(
    document_id: str,
    text: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> str:
    """添加文本块到文档"""
    text_block = {
        "block_type": 2,  # 文本块
        "text": {
            "elements": [
                {
                    "type": "text_run",
                    "text_run": {
                        "content": text
                    }
                }
            ]
        }
    }

    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[text_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if children:
        return children[0].get("block_id")
    return None


def demo_board():
    """演示画板功能"""
    print("=" * 60)
    print("飞书画板（Board）Demo")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 添加说明文本
        print("\n📌 添加说明文本...")
        add_text_block(document_id, "🎨 画板示例：")
        print("   ✅ 说明文本已添加")

        # 添加画板到文档
        print("\n📌 添加画板到文档...")
        board_info = add_board_to_document(document_id, "流程图画板")
        whiteboard_id = board_info.get("whiteboard_id")

        if not whiteboard_id:
            print("   ⚠️ 无法获取 whiteboard_id，跳过节点操作")
        else:
            # 获取画板节点
            print("\n📌 获取画板节点...")
            nodes = get_board_nodes(whiteboard_id)
            print(f"   当前节点数: {len(nodes)}")

            # 创建一些基本图形
            print("\n📌 创建图形节点...")
            
            import time

            # 等待画板数据准备好
            time.sleep(2)

            # 创建矩形（开始）
            node1 = create_board_node(
                whiteboard_id=whiteboard_id,
                shape_type="rect",
                x=100,
                y=100,
                width=120,
                height=60,
                text="开始"
            )

            time.sleep(1)

            # 创建菱形（判断）
            node2 = create_board_node(
                whiteboard_id=whiteboard_id,
                shape_type="diamond",
                x=300,
                y=100,
                width=100,
                height=80,
                text="判断"
            )

            time.sleep(1)

            # 创建椭圆（结束）
            node3 = create_board_node(
                whiteboard_id=whiteboard_id,
                shape_type="ellipse",
                x=500,
                y=100,
                width=120,
                height=60,
                text="结束"
            )

            print(f"\n   ✅ 创建了 {sum(1 for n in [node1, node2, node3] if n)} 个节点")

            # 创建连线
            if node1 and node2 and node3:
                print("\n📌 创建连线...")
                time.sleep(1)

                # 连接开始 -> 判断
                conn1 = create_connector(
                    whiteboard_id=whiteboard_id,
                    start_node_id=node1,
                    end_node_id=node2,
                    shape="straight"
                )

                time.sleep(1)

                # 连接判断 -> 结束
                conn2 = create_connector(
                    whiteboard_id=whiteboard_id,
                    start_node_id=node2,
                    end_node_id=node3,
                    shape="straight"
                )

                print(f"   ✅ 创建了 {sum(1 for c in [conn1, conn2] if c)} 条连线")

        # 添加使用说明
        print("\n📌 添加使用说明...")
        instructions = [
            "",
            "📝 画板功能说明：",
            "- block_type: 43 (Board)",
            "- 支持创建各种图形节点",
            "- 节点类型: rect(矩形), ellipse(椭圆), diamond(菱形) 等",
            "- 可以设置节点位置、大小、文本等属性",
            "",
            "⚠️ 注意：画板需要特殊权限才能创建和操作"
        ]
        for line in instructions:
            add_text_block(document_id, line)
        print("   ✅ 使用说明已添加")

        print("\n✅ Demo 完成")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看画板")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(demo_board())
