#!/usr/bin/env python3
"""
飞书电子表格（Sheet）增删改查工具
API: POST /open-apis/sheets/v3/spreadsheets
     POST /open-apis/sheets/v2/spreadsheets/{spreadsheetToken}/values_append
     GET /open-apis/sheets/v2/spreadsheets/{spreadsheetToken}/values/{range}
     PUT /open-apis/sheets/v2/spreadsheets/{spreadsheetToken}/values
     DELETE /open-apis/sheets/v2/spreadsheets/{spreadsheetToken}/dimension_range
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


def create_spreadsheet(
    title: str,
    folder_token: Optional[str] = None,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建电子表格

    Args:
        title: 表格标题
        folder_token: 文件夹 token（可选）
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        表格信息，包含 spreadsheet_token 和 url
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/sheets/v3/spreadsheets"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {"title": title}
    if folder_token:
        body["folder_token"] = folder_token

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        data = result.get("data", {})
        # 电子表格信息在 spreadsheet 字段中
        spreadsheet = data.get('spreadsheet', {})
        print(f"   ✅ 电子表格创建成功: {title}")
        spreadsheet_token = spreadsheet.get('spreadsheet_token')
        url = spreadsheet.get('url')
        print(f"   Spreadsheet Token: {spreadsheet_token}")
        print(f"   URL: {url}")
        # 将 token 和 url 添加到返回数据中
        data['spreadsheet_token'] = spreadsheet_token
        data['url'] = url
        return data
    else:
        raise Exception(f"创建电子表格失败: {result.get('msg')}")


def get_spreadsheet_info(
    spreadsheet_token: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取电子表格元数据

    Args:
        spreadsheet_token: 表格 token
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        表格元数据
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/metainfo"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers)
    result = resp.json()

    if result.get("code") == 0:
        return result.get("data", {})
    else:
        raise Exception(f"获取表格信息失败: {result.get('msg')}")


# ==================== 增删改查操作 ====================

def append_data(
    spreadsheet_token: str,
    sheet_id: str,
    values: List[List[Any]],
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> bool:
    """
    追加数据到表格（增）

    Args:
        spreadsheet_token: 表格 token
        sheet_id: 工作表 ID
        values: 二维数组，如 [["张三", 28], ["李四", 32]]
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        是否成功
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/values_append"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 使用 sheetId 作为范围，不指定具体单元格
    body = {
        "valueRange": {
            "range": sheet_id,
            "values": values
        }
    }

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        updates = result.get("data", {}).get("updates", {})
        updated_rows = updates.get("updatedRows", 0)
        print(f"   ✅ 数据追加成功，新增 {updated_rows} 行")
        return True
    else:
        print(f"   ❌ 数据追加失败: {result.get('msg')}")
        return False


def read_data(
    spreadsheet_token: str,
    range_str: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> List[List[Any]]:
    """
    读取表格数据（查）

    Args:
        spreadsheet_token: 表格 token
        range_str: 范围，如 "sheetId!A1:C10"
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        二维数组
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/values/{range_str}"
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(url, headers=headers)
    result = resp.json()

    if result.get("code") == 0:
        values = result.get("data", {}).get("valueRange", {}).get("values", [])
        print(f"   ✅ 数据读取成功，共 {len(values)} 行")
        return values
    else:
        print(f"   ❌ 数据读取失败: {result.get('msg')}")
        return []


def write_data(
    spreadsheet_token: str,
    range_str: str,
    values: List[List[Any]],
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> bool:
    """
    写入/更新表格数据（改）

    Args:
        spreadsheet_token: 表格 token
        range_str: 范围，如 "sheetId!A1:B2"
        values: 二维数组
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        是否成功
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    # 使用 values_batch_update 接口
    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/values_batch_update"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "valueRanges": [
            {
                "range": range_str,
                "values": values
            }
        ]
    }

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        updates = result.get("data", {}).get("responses", [{}])[0].get("updatedCells", 0)
        print(f"   ✅ 数据更新成功，更新 {updates} 个单元格")
        return True
    else:
        print(f"   ❌ 数据更新失败: {result.get('msg')}")
        return False


def delete_rows(
    spreadsheet_token: str,
    sheet_id: str,
    start_index: int,
    end_index: int,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> bool:
    """
    删除行（删）

    Args:
        spreadsheet_token: 表格 token
        sheet_id: 工作表 ID
        start_index: 起始行索引（从 0 开始）
        end_index: 结束行索引（不包含）
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        是否成功
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/dimension_range"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "dimension": {
            "sheetId": sheet_id,
            "majorDimension": "ROWS",
            "startIndex": start_index,
            "endIndex": end_index
        }
    }

    resp = requests.delete(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        print(f"   ✅ 行删除成功（第 {start_index + 1} 行到第 {end_index} 行）")
        return True
    else:
        print(f"   ❌ 行删除失败: {result.get('msg')}")
        return False


# ==================== 工作表操作 ====================

def add_sheet(
    spreadsheet_token: str,
    title: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Optional[str]:
    """
    添加工作表

    Args:
        spreadsheet_token: 表格 token
        title: 工作表标题
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        工作表 ID
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "requests": [
            {
                "addSheet": {
                    "properties": {
                        "title": title
                    }
                }
            }
        ]
    }

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        replies = result.get("data", {}).get("replies", [])
        if replies:
            sheet_id = replies[0].get("addSheet", {}).get("properties", {}).get("sheetId")
            print(f"   ✅ 工作表 '{title}' 创建成功")
            return sheet_id
    else:
        print(f"   ❌ 工作表创建失败: {result.get('msg')}")
        return None


def delete_sheet(
    spreadsheet_token: str,
    sheet_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> bool:
    """
    删除工作表

    Args:
        spreadsheet_token: 表格 token
        sheet_id: 工作表 ID
        app_id: 应用 ID
        app_secret: 应用密钥

    Returns:
        是否成功
    """
    _app_id = app_id or APP_ID
    _app_secret = app_secret or APP_SECRET

    token = get_tenant_access_token(_app_id, _app_secret)

    url = f"{BASE_URL}/sheets/v2/spreadsheets/{spreadsheet_token}/sheets_batch_update"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    body = {
        "requests": [
            {
                "deleteSheet": {
                    "sheetId": sheet_id
                }
            }
        ]
    }

    resp = requests.post(url, headers=headers, json=body)
    result = resp.json()

    if result.get("code") == 0:
        print(f"   ✅ 工作表删除成功")
        return True
    else:
        print(f"   ❌ 工作表删除失败: {result.get('msg')}")
        return False


# ==================== 主功能 ====================

def demo_crud():
    """演示增删改查操作"""
    print("=" * 60)
    print("飞书电子表格（Sheet）增删改查工具")
    print("=" * 60)

    try:
        # 1. 创建电子表格
        print("\n📌 步骤 1: 创建电子表格...")
        spreadsheet = create_spreadsheet("员工信息表")
        spreadsheet_token = spreadsheet.get("spreadsheet_token")

        # 获取默认工作表 ID
        info = get_spreadsheet_info(spreadsheet_token)
        sheets = info.get("sheets", [])
        if not sheets:
            raise Exception("无法获取工作表信息")

        sheet_id = sheets[0].get("sheetId")
        sheet_title = sheets[0].get("title")
        print(f"   工作表: {sheet_title} ({sheet_id})")

        # 2. 写入表头（增）
        print("\n📌 步骤 2: 写入表头（增）...")
        headers = [["姓名", "年龄", "部门", "入职日期"]]
        append_data(spreadsheet_token, sheet_id, headers)

        # 3. 写入数据（增）
        print("\n📌 步骤 3: 写入员工数据（增）...")
        employee_data = [
            ["张三", 28, "技术部", "2023-01-15"],
            ["李四", 32, "产品部", "2022-08-20"],
            ["王五", 25, "设计部", "2023-03-10"],
            ["赵六", 30, "市场部", "2021-11-05"]
        ]
        append_data(spreadsheet_token, sheet_id, employee_data)

        # 4. 读取数据（查）
        print("\n📌 步骤 4: 读取所有数据（查）...")
        range_str = f"{sheet_id}!A1:D10"
        data = read_data(spreadsheet_token, range_str)
        for row in data:
            print(f"     {row}")

        # 5. 更新数据（改）
        print("\n📌 步骤 5: 更新张三的年龄（改）...")
        # 使用 range 格式 sheetId!A1:B2
        write_data(spreadsheet_token, f"{sheet_id}!B2:B2", [[29]])

        # 验证更新
        print("\n📌 验证更新...")
        updated_data = read_data(spreadsheet_token, f"{sheet_id}!A2:D2")
        for row in updated_data:
            print(f"     {row}")

        # 6. 删除行（删）
        print("\n📌 步骤 6: 删除第 5 行（赵六）（删）...")
        # 注意：行索引从 0 开始，表头占第 0 行，张三第 1 行，...，赵六第 4 行
        delete_rows(spreadsheet_token, sheet_id, 4, 5)

        # 验证删除
        print("\n📌 验证删除...")
        final_data = read_data(spreadsheet_token, f"{sheet_id}!A1:D10")
        for row in final_data:
            print(f"     {row}")

        # 7. 添加新工作表
        print("\n📌 步骤 7: 添加新工作表...")
        new_sheet_id = add_sheet(spreadsheet_token, "部门统计")
        if new_sheet_id:
            # 向新工作表写入数据
            stats_data = [
                ["部门", "人数"],
                ["技术部", 1],
                ["产品部", 1],
                ["设计部", 1]
            ]
            append_data(spreadsheet_token, new_sheet_id, stats_data)

        print("\n✅ 增删改查演示完成")
        print(f"\n📊 表格 URL: {spreadsheet.get('url')}")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "=" * 60)
    print("完成! 请打开表格查看结果")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(demo_crud())
