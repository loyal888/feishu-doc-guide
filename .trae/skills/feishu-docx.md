# Feishu Docx API Skills

## 概述

本技能集用于指导 AI 使用飞书云文档 (Docx) API 进行文档操作。

## 环境配置

### 必需环境变量

```env
APP_ID=your_feishu_app_id
APP_SECRET=your_feishu_app_secret
```

### 基础导入

```python
import os
import requests
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
BASE_URL = "https://open.feishu.cn/open-apis"
```

## 核心功能

### 1. 获取访问令牌

```python
def get_tenant_access_token(app_id: str, app_secret: str) -> str:
    """获取 tenant_access_token"""
    url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": app_id, "app_secret": app_secret})
    result = resp.json()
    if result.get("code") == 0:
        return result["tenant_access_token"]
    raise Exception(f"获取 token 失败: {result}")
```

### 2. 文档块操作基础

```python
def add_blocks_to_document(
    document_id: str,
    blocks: List[Dict[str, Any]],
    block_id: Optional[str] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """向文档添加块"""
    token = get_tenant_access_token(app_id or APP_ID, app_secret or APP_SECRET)
    parent_block_id = block_id or document_id
    
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{parent_block_id}/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    resp = requests.post(url, headers=headers, json={"children": blocks})
    result = resp.json()
    
    if result.get("code") != 0:
        raise Exception(f"添加块失败: {result.get('msg')}")
    
    return result.get("data", {})
```

## 块类型速查表

| Block Type | 类型值 | 关键字段 | 示例用途 |
|------------|--------|----------|----------|
| Page | 1 | - | 文档根节点 |
| Text | 2 | `text.elements` | 普通文本 |
| Heading1 | 3 | `heading1.elements` | 一级标题 |
| Heading2 | 4 | `heading2.elements` | 二级标题 |
| Heading3 | 5 | `heading3.elements` | 三级标题 |
| Ordered List | 11 | `ordered.elements` | 有序列表 |
| Unordered List | 12 | `unordered.elements` | 无序列表 |
| Table | 14 | `table` | 表格 |
| Table Cell | 15 | `table_cell` | 表格单元格 |
| Quote Container | 16 | `quote_container` | 引用容器 |
| Code Block | 17 | `code` | 代码块 |
| Bitable | 18 | `bitable` | 多维表格 |
| Callout | 19 | `callout.emoji_id` | 高亮块 |
| Chat Card | 20 | `chat_card` | 会话卡片 |
| Divider | 22 | - | 分割线 |
| File | 23 | `file` | 文件附件 |
| Grid | 24 | `grid` | 分栏容器 |
| Grid Column | 25 | `grid_column` | 分栏列 |
| Iframe | 26 | `iframe.url` | 内嵌网页 |
| Image | 27 | `image` | 图片 |
| Table (Docx) | 31 | `table` | 新版表格 |
| Table Cell (Docx) | 32 | `table_cell` | 新版表格单元格 |
| Sheet | 34 | `sheet.token` | 电子表格 |
| AddOns | 35 | `add_ons` | 小组件 |
| Board | 43 | `board.token` | 画板 |

## 常用块结构示例

### 文本块

```python
{
    "block_type": 2,
    "text": {
        "elements": [
            {
                "type": "text_run",
                "text_run": {
                    "content": "文本内容",
                    "text_element_style": {
                        "bold": True,
                        "italic": False,
                        "underline": False,
                        "strikethrough": False
                    }
                }
            }
        ]
    }
}
```

### 高亮块 (Callout)

```python
{
    "block_type": 19,
    "callout": {
        "emoji_id": "bulb",  # 灯泡图标
        "background_color": 1  # 背景色
    }
}
```

### 分割线

```python
{
    "block_type": 22,
    "divider": {}
}
```

### 图片

```python
{
    "block_type": 27,
    "image": {
        "token": "image_token_here",
        "width": 500,
        "height": 300
    }
}
```

### 内嵌块 (Iframe)

```python
{
    "block_type": 26,
    "iframe": {
        "url": "https://example.com",
        "width": 800,
        "height": 600
    }
}
```

### 画板 (Board)

```python
{
    "block_type": 43,
    "board": {
        "title": "画板标题"
    }
}
```

## 电子表格操作

### 创建表格

```python
def create_spreadsheet(title: str) -> Dict[str, Any]:
    """创建电子表格"""
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    url = f"{BASE_URL}/sheets/v3/spreadsheets"
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = requests.post(url, headers=headers, json={"title": title})
    result = resp.json()
    
    if result.get("code") == 0:
        data = result["data"]["spreadsheet"]
        return {
            "spreadsheet_token": data["spreadsheet_token"],
            "url": data["url"]
        }
    raise Exception(f"创建失败: {result}")
```

### 追加数据

```python
def append_data(spreadsheet_token: str, sheet_id: str, values: List[List]):
    """追加数据到表格"""
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/values_append"
    headers = {"Authorization": f"Bearer {token}"}
    
    body = {
        "valueRange": {
            "range": sheet_id,
            "values": values
        }
    }
    
    resp = requests.post(url, headers=headers, json=body)
    return resp.json()
```

### 读取数据

```python
def read_data(spreadsheet_token: str, range_str: str) -> List[List]:
    """读取表格数据"""
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"
    headers = {"Authorization": f"Bearer {token}"}
    
    resp = requests.get(url, headers=headers)
    result = resp.json()
    
    if result.get("code") == 0:
        return result["data"]["valueRange"]["values"]
    return []
```

## 画板操作

### 创建画板节点

```python
def create_board_node(
    whiteboard_id: str,
    shape_type: str,  # rect, ellipse, diamond, etc.
    x: float,
    y: float,
    width: float,
    height: float,
    text: str = ""
) -> str:
    """创建画板图形节点"""
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    url = f"{BASE_URL}/board/v1/whiteboards/{whiteboard_id}/nodes"
    headers = {"Authorization": f"Bearer {token}"}
    
    node_data = {
        "type": "composite_shape",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "composite_shape": {"type": shape_type}
    }
    
    if text:
        node_data["text"] = {
            "text": text,
            "font_size": 14,
            "horizontal_align": "center",
            "vertical_align": "mid"
        }
    
    body = {"nodes": [node_data]}
    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()
    
    if result.get("code") == 0:
        return result["data"]["ids"][0]
    raise Exception(f"创建节点失败: {result}")
```

### 创建连线

```python
def create_connector(
    whiteboard_id: str,
    start_node_id: str,
    end_node_id: str,
    shape: str = "straight"
) -> str:
    """创建画板连线"""
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    url = f"{BASE_URL}/board/v1/whiteboards/{whiteboard_id}/nodes"
    headers = {"Authorization": f"Bearer {token}"}
    
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
                    "position": {"x": 1, "y": 0.5},
                    "snap_to": "right"
                }
            },
            "end": {
                "arrow_style": "line_arrow",
                "attached_object": {
                    "id": end_node_id,
                    "position": {"x": 0, "y": 0.5},
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
        return result["data"]["ids"][0]
    raise Exception(f"创建连线失败: {result}")
```

## 最佳实践

### 1. 错误处理

```python
try:
    result = add_blocks_to_document(document_id, blocks)
    print(f"✅ 成功: {result}")
except Exception as e:
    print(f"❌ 错误: {e}")
```

### 2. 延迟处理

创建画板节点后需要等待数据同步：

```python
import time

# 创建画板
board_info = add_board_to_document(document_id, "流程图")
time.sleep(2)  # 等待画板数据准备好

# 创建节点
node_id = create_board_node(whiteboard_id, "rect", 100, 100, 120, 60)
```

### 3. 获取数据结构

遇到未知的数据结构时，先获取现有数据查看格式：

```python
# 获取画板节点
url = f"{BASE_URL}/board/v1/whiteboards/{whiteboard_id}/nodes"
resp = requests.get(url, headers=headers)
nodes = resp.json()["data"]["nodes"]

# 打印结构
import json
print(json.dumps(nodes, indent=2))
```

## 常见问题

### Q: 如何获取 whiteboard_id？

A: 通过获取文档块接口，查找 block_type 为 43 的块，block.token 就是 whiteboard_id。

### Q: 创建节点返回空 ids？

A: 画板数据可能还没准备好，添加 `time.sleep(2)` 等待后再创建。

### Q: 连线创建失败 "invalid arg"？

A: 检查 connector 结构，position 必须是包含 x, y 的对象，不是数字或字符串。

### Q: 如何设置文档权限？

A: 使用 `set_permission.py` 中的函数，设置 `member_type` 和 `perm` 参数。

## 相关文档

- [飞书云文档 API](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/docx-overview)
- [电子表格 API](https://open.feishu.cn/document/server-docs/docs/sheets-v3/overview)
- [画板 API](https://open.feishu.cn/document/docs/board-v1/overview)
- [多维表格 API](https://open.feishu.cn/document/server-docs/docs/bitable-v1/bitable-overview)
