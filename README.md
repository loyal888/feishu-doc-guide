# Feishu Docx API Toolkit
苦于没有给AI完整操作飞书文档的指南，根据开发文档写了一些例子，喂给AI就能指导AI写、copy文档啦。

飞书云文档 (Docx) API 工具集 - 提供完整的文档操作、块类型管理和增删改查功能。

## 功能特性

### 文档基础操作
- **创建文档** (`create_docx_v1.py`) - 创建飞书云文档
- **权限管理** (`set_permission.py`, `permission_manager.py`) - 设置文档权限
- **读取文档结构** (`get_document_blocks.py`) - 获取文档所有块信息

### 块类型支持

| 块类型 | 文件名 | 功能描述 |
|--------|--------|----------|
| 高亮块 (Callout) | `add_callout.py` | 创建高亮提示块 |
| 表格 (Table) | `add_table.py` | 创建表格并插入内容 |
| 文本 (Text) | `add_text.py` | 创建带样式的文本块 |
| 分割线 (Divider) | `add_divider.py` | 创建分割线 |
| 分栏 (Grid) | `add_grid.py` | 创建多列分栏布局 |
| 内嵌块 (Iframe) | `add_iframe.py` | 嵌入外部网页 |
| 会话卡片 (ChatCard) | `add_chatcard.py` | 插入会话卡片 |
| 图片 (Image) | `add_image.py` | 插入图片 |
| 文件 (File) | `add_file.py` | 插入文件附件 |
| 电子表格 (Sheet) | `sheet_crud.py` | 嵌入电子表格，支持增删改查 |
| 多维表格 (Bitable) | `bitable_crud.py` | 嵌入多维表格，支持增删改查 |
| 画板 (Board) | `board_demo.py` | 嵌入画板，支持图形和连线 |

### 工具模块
- **文件上传** (`upload_file.py`) - 上传媒体文件到飞书
- **API 基础** (`doc_api_base.py`) - 基础 API 调用封装

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

#### 获取应用凭证

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 进入应用详情页，点击「凭证与基础信息」
4. 复制 **App ID** 和 **App Secret**

#### 创建 .env 文件

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的应用凭证：

```env
APP_ID=cli_xxxxxxxxxxxxxxxx
APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. 运行示例

```bash
# 创建文档
python doc-demo/create_docx_v1.py

# 添加高亮块
python doc-demo/add_callout.py

# 添加表格
python doc-demo/add_table.py
```

## AI 使用指南

本项目包含一个 Claude Code Skill，用于指导 AI 操作飞书文档。

### Skill 结构

```
skills/feishu-doc-operator/
├── skill.md              # AI 技能指导文档
└── scripts/              # 脚本文件目录
    ├── create_docx_v1.py
    ├── upload_file.py
    ├── sheet_crud.py
    ├── bitable_crud.py
    ├── board_demo.py
    └── ...
```

### 指导 AI 使用

将 `skills/feishu-doc-operator/` 目录配置到 Claude Code 的 skills 路径中，AI 即可根据 `skill.md` 中的指导：

1. **创建文档**
   ```python
   from scripts.create_docx_v1 import create_document
   doc = create_document("文档标题")
   ```

2. **添加块**
   ```python
   from scripts.upload_file import get_tenant_access_token
   # 使用 add_blocks_to_document 添加各种块
   ```

3. **操作电子表格**
   ```python
   from scripts.sheet_crud import create_spreadsheet, append_data
   ```

4. **操作画板**
   ```python
   from scripts.board_demo import add_board_to_document, create_board_node
   ```

### 配置 Claude Code Skills

在项目根目录创建 `.claude/skills/` 目录，将 `feishu-doc-operator` 放入其中：

```bash
mkdir -p .claude/skills
cp -r skills/feishu-doc-operator .claude/skills/
```

或在 Claude Code 配置中添加 skills 路径指向 `skills/` 目录。

## 项目结构

```
feishu-docx-toolkit/
├── doc-demo/              # 示例脚本目录
│   ├── create_docx_v1.py      # 文档创建
│   ├── set_permission.py      # 权限设置
│   ├── get_document_blocks.py # 读取文档结构
│   ├── upload_file.py         # 文件上传工具
│   ├── doc_api_base.py        # API 基础封装
│   ├── add_callout.py         # 高亮块
│   ├── add_table.py           # 表格
│   ├── add_text.py            # 文本块
│   ├── add_divider.py         # 分割线
│   ├── add_grid.py            # 分栏
│   ├── add_iframe.py          # 内嵌块
│   ├── add_chatcard.py        # 会话卡片
│   ├── add_image.py           # 图片
│   ├── add_file.py            # 文件
│   ├── sheet_crud.py          # 电子表格增删改查
│   ├── bitable_crud.py        # 多维表格增删改查
│   ├── board_demo.py          # 画板
│   └── get_board_nodes.py     # 获取画板节点
│
├── skills/                # Claude Code Skills
│   └── feishu-doc-operator/   # 飞书文档操作 Skill
│       ├── skill.md           # AI 技能指导文档
│       └── scripts/           # Skill 脚本目录
│           ├── create_docx_v1.py
│           ├── upload_file.py
│           ├── sheet_crud.py
│           ├── bitable_crud.py
│           ├── board_demo.py
│           └── ...
│
├── README.md              # 项目说明
├── .env.example           # 环境变量模板
├── .gitignore             # Git 忽略配置
└── requirements.txt       # Python 依赖
```

## API 参考

### 文档块类型 (Block Types)

| 类型值 | 名称 | 说明 |
|--------|------|------|
| 1 | Page | 页面根节点 |
| 2 | Text | 文本块 |
| 3 | Heading1-9 | 标题 1-9 |
| 11 | Ordered List | 有序列表 |
| 12 | Unordered List | 无序列表 |
| 14 | Table | 表格 |
| 15 | Table Cell | 表格单元格 |
| 18 | Bitable | 多维表格 |
| 19 | Callout | 高亮块 |
| 22 | Divider | 分割线 |
| 23 | File | 文件 |
| 24 | Grid | 分栏容器 |
| 25 | Grid Column | 分栏列 |
| 26 | Iframe | 内嵌块 |
| 27 | Image | 图片 |
| 31 | Table | 表格 (Docx) |
| 32 | Table Cell | 表格单元格 (Docx) |
| 34 | Sheet | 电子表格 |
| 43 | Board | 画板 |

### 电子表格操作

```python
from sheet_crud import create_spreadsheet, append_data, read_data, write_data, delete_rows

# 创建表格
spreadsheet = create_spreadsheet("员工信息表")
token = spreadsheet["spreadsheet_token"]

# 写入数据
append_data(token, sheet_id, [["姓名", "年龄"], ["张三", 28]])

# 读取数据
data = read_data(token, f"{sheet_id}!A1:B10")

# 更新数据
write_data(token, f"{sheet_id}!B2:B2", [[29]])

# 删除行
delete_rows(token, sheet_id, 2, 3)
```

### 多维表格操作

```python
from bitable_crud import create_record, list_records, update_record, delete_record

# 创建记录
create_record(bitable_token, {"姓名": "张三", "年龄": 28})

# 查询记录
records = list_records(bitable_token)

# 更新记录
update_record(bitable_token, record_id, {"年龄": 29})

# 删除记录
delete_record(bitable_token, record_id)
```

### 画板操作

```python
from board_demo import add_board_to_document, create_board_node, create_connector

# 添加画板
board_info = add_board_to_document(document_id, "流程图")
whiteboard_id = board_info["whiteboard_id"]

# 创建节点
node1 = create_board_node(whiteboard_id, "rect", 100, 100, 120, 60, "开始")
node2 = create_board_node(whiteboard_id, "diamond", 300, 100, 100, 80, "判断")

# 创建连线
create_connector(whiteboard_id, node1, node2, "straight")
```

## 开发指南

### 添加新的块类型

1. 创建新的 Python 文件 `add_<block_type>.py`
2. 导入基础模块：`from upload_file import get_tenant_access_token`
3. 实现块创建函数
4. 添加示例代码到 `if __name__ == "__main__"`

### 块结构示例

```python
block = {
    "block_type": 19,  # Callout
    "callout": {
        "emoji_id": "bulb",
        "background_color": 1
    }
}
```

## 注意事项

1. **权限要求**：应用需要申请相应的云文档权限
2. **频率限制**：API 调用有频率限制，注意控制请求频率
3. **Token 有效期**：tenant_access_token 有效期约 2 小时，会自动刷新
4. **错误处理**：所有 API 调用都应处理可能的错误情况

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [飞书开放平台](https://open.feishu.cn/)
- [云文档 API 文档](https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/docx-overview)
- [电子表格 API 文档](https://open.feishu.cn/document/server-docs/docs/sheets-v3/overview)
- [画板 API 文档](https://open.feishu.cn/document/docs/board-v1/overview)
