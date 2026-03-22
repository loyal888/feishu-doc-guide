# Feishu Doc Operator - AI Skill Guide

## 概述

本技能用于指导 AI 操作飞书云文档 (Docx)，支持创建文档、添加各种块类型、管理权限等功能。

## 前置条件

1. 环境变量已配置：
   - `APP_ID` - 飞书应用 ID
   - `APP_SECRET` - 飞书应用密钥

2. 依赖已安装：
   ```bash
   pip install requests python-dotenv
   ```

## 核心能力

### 1. 创建文档

```python
from doc_demo.create_docx_v1 import create_document

# 创建文档
doc = create_document("文档标题", folder_token="可选文件夹token")
document_id = doc["document_id"]
url = doc["url"]
```

### 2. 添加块到文档

#### 基础方法

```python
from doc_demo.upload_file import get_tenant_access_token
import requests

def add_block(document_id, block_data):
    token = get_tenant_access_token(APP_ID, APP_SECRET)
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/blocks/{document_id}/children"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"children": [block_data]})
    return resp.json()
```

#### 常用块类型

**文本块**
```python
{
    "block_type": 2,
    "text": {
        "elements": [{"type": "text_run", "text_run": {"content": "文本内容"}}]
    }
}
```

**高亮块**
```python
{
    "block_type": 19,
    "callout": {"emoji_id": "bulb", "background_color": 1}
}
```

**分割线**
```python
{"block_type": 22, "divider": {}}
```

**图片**
```python
{
    "block_type": 27,
    "image": {"token": "image_token", "width": 500, "height": 300}
}
```

**表格**
```python
{
    "block_type": 31,
    "table": {
        "row_size": 2,
        "column_size": 2,
        "table_cells": [...]
    }
}
```

### 3. 电子表格操作

```python
from doc_demo.sheet_crud import create_spreadsheet, append_data, read_data

# 创建表格
sheet = create_spreadsheet("表格标题")
token = sheet["spreadsheet_token"]

# 写入数据
append_data(token, sheet_id, [["姓名", "年龄"], ["张三", 28]])

# 读取数据
data = read_data(token, f"{sheet_id}!A1:B10")
```

### 4. 多维表格操作

```python
from doc_demo.bitable_crud import create_record, list_records, update_record, delete_record

# 创建记录
create_record(bitable_token, {"姓名": "张三", "年龄": 28})

# 查询记录
records = list_records(bitable_token)

# 更新记录
update_record(bitable_token, record_id, {"年龄": 29})

# 删除记录
delete_record(bitable_token, record_id)
```

### 5. 画板操作

```python
from doc_demo.board_demo import add_board_to_document, create_board_node, create_connector
import time

# 添加画板
board = add_board_to_document(document_id, "流程图")
whiteboard_id = board["whiteboard_id"]

# 等待画板准备好
time.sleep(2)

# 创建节点
node1 = create_board_node(whiteboard_id, "rect", 100, 100, 120, 60, "开始")
node2 = create_board_node(whiteboard_id, "diamond", 300, 100, 100, 80, "判断")

# 创建连线
create_connector(whiteboard_id, node1, node2)
```

## 块类型速查

| 类型 | 值 | 用途 |
|------|-----|------|
| Page | 1 | 页面根节点 |
| Text | 2 | 文本块 |
| Heading1-9 | 3-11 | 标题 |
| Ordered List | 12 | 有序列表 |
| Unordered List | 13 | 无序列表 |
| Table | 14/31 | 表格 |
| Bitable | 18 | 多维表格 |
| Callout | 19 | 高亮块 |
| Divider | 22 | 分割线 |
| File | 23 | 文件 |
| Grid | 24 | 分栏 |
| Iframe | 26 | 内嵌网页 |
| Image | 27 | 图片 |
| Sheet | 34 | 电子表格 |
| Board | 43 | 画板 |

## 最佳实践

1. **错误处理**：所有 API 调用都要处理异常
2. **延迟处理**：创建画板节点后等待 1-2 秒
3. **数据结构**：不确定时先获取现有数据查看结构
4. **权限设置**：新文档需要设置权限才能被访问

## 调试技巧

```python
import json

# 打印 API 响应
print(json.dumps(result, indent=2, ensure_ascii=False))

# 获取画板节点查看结构
from doc_demo.get_board_nodes import get_board_nodes
nodes = get_board_nodes(whiteboard_id)
print(json.dumps(nodes, indent=2))
```

## 参考文档

- [飞书开放平台](https://open.feishu.cn/)
- [云文档 API](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/docx-overview)
- [电子表格 API](https://open.feishu.cn/document/server-docs/docs/sheets-v3/overview)
- [画板 API](https://open.feishu.cn/document/docs/board-v1/overview)
