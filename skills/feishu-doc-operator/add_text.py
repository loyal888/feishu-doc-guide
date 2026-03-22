#!/usr/bin/env python3
"""
飞书文档文本块样式演示
支持：粗体、斜体、下划线、删除线、代码、颜色等样式
API: POST /open-apis/docx/v1/documents/{document_id}/blocks/{block_id}/children
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


def create_text_element(
    content: str,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    strikethrough: bool = False,
    inline_code: bool = False,
    text_color: Optional[int] = None,
    background_color: Optional[int] = None,
    link: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建文本元素（带样式）
    
    Args:
        content: 文本内容
        bold: 粗体
        italic: 斜体
        underline: 下划线
        strikethrough: 删除线
        inline_code: 行内代码
        text_color: 字体颜色 (1-7)
        background_color: 背景颜色 (1-14)
        link: 链接 URL
    
    Returns:
        文本元素字典
    """
    text_element = {
        "type": "text_run",
        "text_run": {
            "content": content,
            "text_element_style": {}
        }
    }
    
    style = text_element["text_run"]["text_element_style"]
    
    if bold:
        style["bold"] = True
    if italic:
        style["italic"] = True
    if underline:
        style["underline"] = True
    if strikethrough:
        style["strikethrough"] = True
    if inline_code:
        style["inline_code"] = True
    if text_color is not None:
        style["text_color"] = text_color
    if background_color is not None:
        style["background_color"] = background_color
    if link:
        style["link"] = {"url": link}
    
    return text_element


def create_text_block(
    elements: List[Dict[str, Any]],
    align: int = 1
) -> Dict[str, Any]:
    """
    创建文本块
    
    Args:
        elements: 文本元素列表
        align: 对齐方式 (1=左对齐, 2=居中, 3=右对齐)
    
    Returns:
        文本块字典
    """
    return {
        "block_type": 2,
        "text": {
            "elements": elements,
            "style": {
                "align": align
            }
        }
    }


def add_styled_text_demo(
    document_id: str,
    app_id: Optional[str] = None,
    app_secret: Optional[str] = None
) -> Dict[str, Any]:
    """
    添加带样式的文本演示
    
    演示各种文本样式：粗体、斜体、下划线、删除线、代码、颜色等
    """
    print("\n📌 创建各种样式的文本块...")
    
    blocks = []
    
    # 1. 普通文本
    print("   添加普通文本...")
    blocks.append(create_text_block([
        create_text_element("这是普通文本")
    ]))
    
    # 2. 粗体
    print("   添加粗体文本...")
    blocks.append(create_text_block([
        create_text_element("这是粗体文本", bold=True)
    ]))
    
    # 3. 斜体
    print("   添加斜体文本...")
    blocks.append(create_text_block([
        create_text_element("这是斜体文本", italic=True)
    ]))
    
    # 4. 粗体 + 斜体
    print("   添加粗斜体文本...")
    blocks.append(create_text_block([
        create_text_element("这是粗斜体文本", bold=True, italic=True)
    ]))
    
    # 5. 下划线
    print("   添加下划线文本...")
    blocks.append(create_text_block([
        create_text_element("这是下划线文本", underline=True)
    ]))
    
    # 6. 删除线
    print("   添加删除线文本...")
    blocks.append(create_text_block([
        create_text_element("这是删除线文本", strikethrough=True)
    ]))
    
    # 7. 行内代码
    print("   添加行内代码...")
    blocks.append(create_text_block([
        create_text_element("这是普通文本，"),
        create_text_element("print('Hello World')", inline_code=True),
        create_text_element(" 这是代码")
    ]))
    
    # 8. 彩色文本
    print("   添加彩色文本...")
    blocks.append(create_text_block([
        create_text_element("红色文本 ", text_color=1),
        create_text_element("橙色文本 ", text_color=2),
        create_text_element("黄色文本 ", text_color=3),
        create_text_element("绿色文本 ", text_color=4),
        create_text_element("蓝色文本 ", text_color=5),
        create_text_element("紫色文本 ", text_color=6),
        create_text_element("灰色文本", text_color=7)
    ]))
    
    # 9. 背景色
    print("   添加背景色文本...")
    blocks.append(create_text_block([
        create_text_element("浅黄背景", background_color=3),
        create_text_element(" "),
        create_text_element("浅绿背景", background_color=4),
        create_text_element(" "),
        create_text_element("浅蓝背景", background_color=5)
    ]))
    
    # 10. 链接
    print("   添加链接...")
    blocks.append(create_text_block([
        create_text_element("访问 "),
        create_text_element("飞书开放平台", link="https://open.feishu.cn"),
        create_text_element(" 了解更多")
    ]))
    
    # 11. 混合样式
    print("   添加混合样式文本...")
    blocks.append(create_text_block([
        create_text_element("这是一段"),
        create_text_element("粗体", bold=True),
        create_text_element("和"),
        create_text_element("斜体", italic=True),
        create_text_element("和"),
        create_text_element("下划线", underline=True),
        create_text_element("和"),
        create_text_element("删除线", strikethrough=True),
        create_text_element("的混合样式文本，"),
        create_text_element("还可以带颜色", bold=True, text_color=5),
        create_text_element("！")
    ]))
    
    # 12. 居中对齐
    print("   添加居中对齐文本...")
    blocks.append(create_text_block([
        create_text_element("这是居中对齐的文本", bold=True)
    ], align=2))
    
    # 13. 右对齐
    print("   添加右对齐文本...")
    blocks.append(create_text_block([
        create_text_element("这是右对齐的文本", italic=True)
    ], align=3))
    
    # 批量添加所有文本块
    result = add_blocks_to_document(
        document_id=document_id,
        blocks=blocks,
        app_id=app_id,
        app_secret=app_secret
    )
    
    children = result.get("children", [])
    block_ids = [child.get("block_id") for child in children]
    
    print(f"✅ 成功添加 {len(block_ids)} 个文本块")
    
    return {
        "block_ids": block_ids,
        "count": len(block_ids)
    }


def main():
    """主函数"""
    print("=" * 60)
    print("飞书文档文本样式演示工具")
    print("=" * 60)
    
    document_id = "SZPFdznFzo45B8xSYJpcexc2nje"
    print(f"\n📝 文档 ID: {document_id}")
    
    try:
        result = add_styled_text_demo(
            document_id=document_id
        )
        
        print(f"\n📋 结果:")
        print(f"   添加了 {result['count']} 个文本块")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "=" * 60)
    print("完成! 请刷新文档查看各种文本样式")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    exit(main())
