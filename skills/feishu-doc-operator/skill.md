---
name: feishu-doc-operator
description: >
  操作飞书云文档 (Docx) API，支持创建文档、添加各种块类型（文本、表格、图片、画板等）、
  电子表格增删改查、多维表格管理、权限设置等功能。
  适用于需要自动化处理飞书文档的场景。

# 触发条件 - 当用户提到以下关键词时激活此技能
when_to_use:
  - 飞书文档
  - 创建文档
  - 添加块
  - 表格操作
  - 画板
  - 文档权限
  - bitable
  - sheet
  - board
  - docx

# 需要的工具/权限
tools:
  - python
  - requests
  - file_system

# 依赖文件
dependencies:
  - scripts/create_docx_v1.py
  - scripts/upload_file.py
  - scripts/sheet_crud.py
  - scripts/bitable_crud.py
  - scripts/board_demo.py
  - scripts/set_permission.py
---

# Feishu Doc Operator Skill

## 快速开始

### 1. 检查环境

确保 `.env` 文件存在且包含：
```
APP_ID=cli_xxxxxxxxxxxxxxxx
APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. 导入模块

```python
from scripts.upload_file import get_tenant_access_token
import requests
import os

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")
BASE_URL = "https://open.feishu.cn/open-apis"
```

## 核心操作

### 创建文档

```python
from scripts.create_docx_v1 import create_document

doc = create_document("文档标题")
document_id = doc["document_id"]
print(f"文档创建成功: {doc['url']}")
```

### 添加块到文档

**基础函数：**
```python
def add_blocks(document_id, blocks):
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    url = f"{BASE_URL}/docx/v1/documents/{document_id}/blocks/{document_id}/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"children": blocks})
    return resp.json()
```

**添加文本：**
```python
add_blocks(document_id, [{
    "block_type": 2,
    "text": {
        "elements": [{"type": "text_run", "text_run": {"content": "Hello World"}}]
    }
}])
```

**添加分割线：**
```python
add_blocks(document_id, [{"block_type": 22, "divider": {}}])
```

**添加高亮块：**
```python
add_blocks(document_id, [{
    "block_type": 19,
    "callout": {"emoji_id": "bulb", "background_color": 1}
}])
```

### 电子表格操作

```python
from scripts.sheet_crud import create_spreadsheet, append_data, read_data

# 创建
sheet = create_spreadsheet("员工表")
token = sheet["spreadsheet_token"]

# 写入
append_data(token, sheet_id, [["姓名", "年龄"], ["张三", 28]])

# 读取
data = read_data(token, f"{sheet_id}!A1:B10")
```

### 多维表格操作

```python
from scripts.bitable_crud import create_record, list_records, update_record, delete_record

# 增
create_record(bitable_token, {"姓名": "张三", "年龄": 28})

# 查
records = list_records(bitable_token)

# 改
update_record(bitable_token, record_id, {"年龄": 29})

# 删
delete_record(bitable_token, record_id)
```

### 画板操作

```python
from scripts.board_demo import add_board_to_document, create_board_node, create_connector
import time

# 添加画板
board = add_board_to_document(document_id, "流程图")
whiteboard_id = board["whiteboard_id"]

# 等待数据同步
time.sleep(2)

# 创建节点
node1 = create_board_node(whiteboard_id, "rect", 100, 100, 120, 60, "开始")
node2 = create_board_node(whiteboard_id, "diamond", 300, 100, 100, 80, "判断")

# 创建连线
create_connector(whiteboard_id, node1, node2, "straight")
```

## 块类型速查

| 类型 | 值 | 关键字段 |
|------|-----|----------|
| Page | 1 | - |
| Text | 2 | `text.elements` |
| Heading1-9 | 3-11 | `headingX.elements` |
| Table | 14/31 | `table` |
| Bitable | 18 | `bitable` |
| Callout | 19 | `callout.emoji_id` |
| Divider | 22 | - |
| File | 23 | `file` |
| Grid | 24 | `grid` |
| Iframe | 26 | `iframe.url` |
| Image | 27 | `image.token` |
| Sheet | 34 | `sheet.token` |
| Board | 43 | `board.token` |

## 最佳实践

1. **错误处理**：所有 API 调用都要 try-except
2. **画板延迟**：创建节点前 sleep 1-2 秒
3. **数据结构**：不确定时先用 get_board_nodes 查看
4. **权限**：新文档需要 set_permission 设置权限

## 调试

```python
import json

# 打印完整响应
print(json.dumps(result, indent=2, ensure_ascii=False))

# 查看画板节点结构
from scripts.get_board_nodes import get_board_nodes
nodes = get_board_nodes(whiteboard_id)
print(json.dumps(nodes, indent=2))
```

## 参考

- [飞书开放平台](https://open.feishu.cn/)
- [云文档 API](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/docx-overview)
