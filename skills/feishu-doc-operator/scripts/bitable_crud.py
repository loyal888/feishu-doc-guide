#!/usr/bin/env python3
"""
飞书文档多维表格（Bitable）增删改查工具
支持 Grid view（数据表视图）
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
     POST /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records
     GET /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records
     PUT /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
     DELETE /open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}
"""

import os
import requests
import time
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


def parse_bitable_token(bitable_token: str) -> tuple:
    """解析 bitable_token，返回 (app_token, table_id)"""
    parts = bitable_token.split("_")
    if len(parts) < 2:
        raise ValueError(f"无效的 bitable_token: {bitable_token}")
    return parts[0], parts[1]


# ==================== 增删改查操作 ====================

def create_record(
    bitable_token: str,
    fields: Dict[str, Any],
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Optional[str]:
    """
    创建记录（增）

    Args:
        bitable_token: Bitable Token
        fields: 字段值字典，如 {"姓名": "张三", "年龄": 28}
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        记录 ID，失败返回 None
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    app_token, table_id = parse_bitable_token(bitable_token)
    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.post(url, headers=headers, json={"fields": fields})
    result = resp.json()

    if result.get("code") == 0:
        record_id = result.get("data", {}).get("record", {}).get("record_id")
        print(f"   ✅ 记录创建成功: {record_id}")
        return record_id
    else:
        print(f"   ❌ 记录创建失败: {result.get('msg')}")
        return None


def list_records(
    bitable_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    查询记录（查）

    Args:
        bitable_token: Bitable Token
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        记录列表
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    app_token, table_id = parse_bitable_token(bitable_token)
    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers)
    result = resp.json()

    if result.get("code") == 0:
        records = result.get("data", {}).get("items", [])
        print(f"   ✅ 查询到 {len(records)} 条记录")
        return records
    else:
        print(f"   ❌ 查询失败: {result.get('msg')}")
        return []


def update_record(
    bitable_token: str,
    record_id: str,
    fields: Dict[str, Any],
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> bool:
    """
    更新记录（改）

    Args:
        bitable_token: Bitable Token
        record_id: 记录 ID
        fields: 要更新的字段值
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        是否成功
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    app_token, table_id = parse_bitable_token(bitable_token)
    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    resp = requests.put(url, headers=headers, json={"fields": fields})
    result = resp.json()

    if result.get("code") == 0:
        print(f"   ✅ 记录更新成功: {record_id}")
        return True
    else:
        print(f"   ❌ 记录更新失败: {result.get('msg')}")
        return False


def delete_record(
    bitable_token: str,
    record_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> bool:
    """
    删除记录（删）

    Args:
        bitable_token: Bitable Token
        record_id: 记录 ID
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        是否成功
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    app_token, table_id = parse_bitable_token(bitable_token)
    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/records/{record_id}"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.delete(url, headers=headers)
    result = resp.json()

    if result.get("code") == 0:
        print(f"   ✅ 记录删除成功: {record_id}")
        return True
    else:
        print(f"   ❌ 记录删除失败: {result.get('msg')}")
        return False


# ==================== 字段操作 ====================

def add_field(
    bitable_token: str,
    field_name: str,
    field_type: int,
    property: Optional[Dict] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Optional[str]:
    """
    添加字段

    Args:
        bitable_token: Bitable Token
        field_name: 字段名
        field_type: 字段类型，1=文本, 2=数字等
        property: 字段属性
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        字段 ID，失败返回 None
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    app_token, table_id = parse_bitable_token(bitable_token)
    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "field_name": field_name,
        "type": field_type
    }
    if property:
        body["property"] = property

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        field_id = result.get("data", {}).get("field", {}).get("field_id")
        print(f"   ✅ 字段 '{field_name}' 创建成功")
        return field_id
    else:
        print(f"   ❌ 字段 '{field_name}' 创建失败: {result.get('msg')}")
        return None


def get_fields(
    bitable_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, str]:
    """
    获取字段列表

    Args:
        bitable_token: Bitable Token
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        字段名到字段 ID 的映射
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    app_token, table_id = parse_bitable_token(bitable_token)
    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers)
    result = resp.json()

    field_map = {}
    if result.get("code") == 0:
        fields = result.get("data", {}).get("items", [])
        for field in fields:
            field_name = field.get("field_name")
            field_id = field.get("field_id")
            if field_name and field_id:
                field_map[field_name] = field_id

    return field_map


def delete_field(
    bitable_token: str,
    field_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> bool:
    """
    删除字段（列）

    Args:
        bitable_token: Bitable Token
        field_id: 字段 ID
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        是否成功
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    app_token, table_id = parse_bitable_token(bitable_token)
    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/bitable/v1/apps/{app_token}/tables/{table_id}/fields/{field_id}"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.delete(url, headers=headers)
    result = resp.json()

    if result.get("code") == 0:
        print(f"   ✅ 字段删除成功: {field_id}")
        return True
    else:
        print(f"   ❌ 字段删除失败: {result.get('msg')}")
        return False


# ==================== 主功能 ====================

def create_bitable_with_data(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Optional[str]:
    """
    创建多维表格并添加测试数据

    Returns:
        bitable_token
    """
    print("\n📌 创建多维表格（Grid view）...")

    # 1. 创建多维表格块
    bitable_block = {
        "block_type": 18,  # Bitable 块
        "bitable": {
            "view_type": 1  # Grid view（数据表）
        }
    }

    result = add_blocks_to_document(
        document_id=document_id,
        blocks=[bitable_block],
        app_id=app_id,
        app_secret=app_secret
    )

    children = result.get("children", [])
    if not children:
        raise Exception("创建多维表格失败")

    bitable_block_id = children[0].get("block_id")
    bitable_token = children[0].get("bitable", {}).get("token", "")

    print(f"   ✅ 多维表格创建成功")
    print(f"   Block ID: {bitable_block_id}")
    print(f"   Bitable Token: {bitable_token}")

    # 2. 添加字段
    print("\n   添加字段...")
    add_field(bitable_token, "姓名", 1, app_id=app_id, app_secret=app_secret)
    add_field(bitable_token, "年龄", 2, {"formatter": "0"}, app_id=app_id, app_secret=app_secret)
    add_field(bitable_token, "部门", 1, app_id=app_id, app_secret=app_secret)

    # 等待字段同步
    time.sleep(1)

    # 3. 添加记录（增）
    print("\n   添加记录（增）...")
    record_ids = []
    rid = create_record(bitable_token, {"姓名": "张三", "年龄": 28, "部门": "技术部"}, app_id, app_secret)
    if rid:
        record_ids.append(rid)
    rid = create_record(bitable_token, {"姓名": "李四", "年龄": 32, "部门": "产品部"}, app_id, app_secret)
    if rid:
        record_ids.append(rid)
    rid = create_record(bitable_token, {"姓名": "王五", "年龄": 25, "部门": "设计部"}, app_id, app_secret)
    if rid:
        record_ids.append(rid)

    return bitable_token, record_ids


def demo_crud(
    bitable_token: str,
    record_ids: List[str],
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
):
    """演示增删改查操作"""

    # 查
    print("\n   查询记录（查）...")
    records = list_records(bitable_token, app_id, app_secret)
    for record in records:
        fields = record.get("fields", {})
        print(f"     - {fields}")

    # 改
    if record_ids:
        print("\n   更新记录（改）...")
        update_record(
            bitable_token,
            record_ids[0],
            {"姓名": "张三（已更新）", "年龄": 29},
            app_id,
            app_secret
        )

        # 查验证更新
        print("\n   查询验证更新...")
        records = list_records(bitable_token, app_id, app_secret)
        for record in records[:1]:
            fields = record.get("fields", {})
            print(f"     - {fields}")

    # 删
    if len(record_ids) > 2:
        print("\n   删除记录（删）...")
        delete_record(bitable_token, record_ids[2], app_id, app_secret)

        # 查验证删除
        print("\n   查询验证删除...")
        records = list_records(bitable_token, app_id, app_secret)
        print(f"     剩余 {len(records)} 条记录")

    # 删除"姓名"列（我们创建的第一个字段）
    print("\n   删除'姓名'列...")
    fields = get_fields(bitable_token, app_id, app_secret)
    if "姓名" in fields:
        field_id = fields["姓名"]
        print(f"     字段: 姓名 ({field_id})")
        delete_field(bitable_token, field_id, app_id, app_secret)

        # 查验证列删除
        print("\n   查询验证列删除...")
        remaining_fields = get_fields(bitable_token, app_id, app_secret)
        print(f"     剩余字段: {list(remaining_fields.keys())}")
    else:
        print("     未找到'姓名'字段")


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档多维表格（Bitable）增删改查工具")
    print("=" * 60)

    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")

    try:
        # 创建多维表格并添加数据
        bitable_token, record_ids = create_bitable_with_data(document_id)

        # 演示增删改查
        demo_crud(bitable_token, record_ids)

        print("\n✅ 增删改查演示完成")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看多维表格")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
