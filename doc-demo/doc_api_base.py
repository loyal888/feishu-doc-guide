#!/usr/bin/env python3
"""
飞书云文档 API 基础封装
基础功能：认证、请求发送、错误处理
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 飞书应用配置
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# API 基础配置
BASE_URL = "https://open.feishu.cn/open-apis"


@dataclass
class DocBlock:
    """文档块数据结构"""
    block_id: str
    block_type: int
    parent_id: str
    children: List[str]
    content: Dict[str, Any]


class FeishuDocAPI:
    """飞书云文档 API 客户端"""
    
    # 块类型常量
    BLOCK_TYPE_PAGE = 1
    BLOCK_TYPE_TEXT = 2
    BLOCK_TYPE_HEADING1 = 3
    BLOCK_TYPE_HEADING2 = 4
    BLOCK_TYPE_HEADING3 = 5
    BLOCK_TYPE_BULLET = 6
    BLOCK_TYPE_ORDERED = 7
    BLOCK_TYPE_TODO = 8
    BLOCK_TYPE_TABLE = 9
    BLOCK_TYPE_QUOTE = 10
    BLOCK_TYPE_CODE = 11
    BLOCK_TYPE_DIVIDER = 12
    BLOCK_TYPE_IMAGE = 13
    BLOCK_TYPE_FILE = 14
    
    def __init__(self, app_id: str = None, app_secret: str = None):
        """
        初始化 API 客户端
        
        Args:
            app_id: 应用 ID，默认从环境变量读取
            app_secret: 应用密钥，默认从环境变量读取
        """
        self.app_id = app_id or APP_ID
        self.app_secret = app_secret or APP_SECRET
        self._tenant_access_token: Optional[str] = None
        
        if not self.app_id or not self.app_secret:
            raise ValueError("缺少 APP_ID 或 APP_SECRET，请检查 .env 文件")
    
    def _get_tenant_access_token(self) -> str:
        """获取 tenant_access_token（带缓存）"""
        if self._tenant_access_token:
            return self._tenant_access_token
        
        url = f"{BASE_URL}/auth/v3/tenant_access_token/internal"
        headers = {"Content-Type": "application/json"}
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        resp = requests.post(url, headers=headers, json=data)
        result = resp.json()
        
        if result.get("code") != 0:
            raise Exception(f"获取 token 失败: {result}")
        
        self._tenant_access_token = result["tenant_access_token"]
        return self._tenant_access_token
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        token = self._get_tenant_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送 API 请求
        
        Args:
            method: HTTP 方法 (GET/POST/PATCH/DELETE)
            endpoint: API 端点路径
            **kwargs: 其他请求参数
        
        Returns:
            API 响应数据
        """
        url = f"{BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        # 如果有自定义 headers，合并
        if "headers" in kwargs:
            headers.update(kwargs.pop("headers"))
        
        resp = requests.request(method, url, headers=headers, **kwargs)
        
        # 处理限频
        if resp.status_code == 400 and resp.json().get("code") == 99991400:
            raise Exception("请求过于频繁，请稍后重试")
        
        result = resp.json()
        
        if result.get("code") != 0:
            error_msg = result.get("msg", "未知错误")
            error_code = result.get("code")
            raise Exception(f"API 错误 [{error_code}]: {error_msg}")
        
        return result.get("data", {})
    
    # ============ 文档操作 ============
    
    def create_document(self, title: str, folder_token: str = None) -> Dict[str, Any]:
        """
        创建新文档
        
        Args:
            title: 文档标题
            folder_token: 文件夹 token（可选）
        
        Returns:
            包含 document_id 等信息的字典
        """
        endpoint = "/docx/v1/documents"
        body = {"title": title}
        if folder_token:
            body["folder_token"] = folder_token
        
        return self._request("POST", endpoint, json=body)
    
    def get_document(self, document_id: str) -> Dict[str, Any]:
        """
        获取文档基本信息
        
        Args:
            document_id: 文档 ID
        
        Returns:
            文档信息字典
        """
        endpoint = f"/docx/v1/documents/{document_id}"
        return self._request("GET", endpoint)
    
    # ============ 块操作 ============
    
    def get_blocks(self, document_id: str, page_token: str = None, page_size: int = 500) -> Dict[str, Any]:
        """
        获取文档所有块
        
        Args:
            document_id: 文档 ID
            page_token: 分页 token
            page_size: 每页大小（最大 500）
        
        Returns:
            块列表数据
        """
        endpoint = f"/docx/v1/documents/{document_id}/blocks"
        params = {"page_size": page_size}
        if page_token:
            params["page_token"] = page_token
        
        return self._request("GET", endpoint, params=params)
    
    def get_all_blocks(self, document_id: str) -> List[DocBlock]:
        """
        获取文档所有块（自动分页）
        
        Args:
            document_id: 文档 ID
        
        Returns:
            DocBlock 对象列表
        """
        all_blocks = []
        page_token = None
        
        while True:
            result = self.get_blocks(document_id, page_token)
            items = result.get("items", [])
            
            for item in items:
                block = DocBlock(
                    block_id=item.get("block_id"),
                    block_type=item.get("block_type"),
                    parent_id=item.get("parent_id"),
                    children=item.get("children", []),
                    content=item
                )
                all_blocks.append(block)
            
            page_token = result.get("page_token")
            if not page_token:
                break
        
        return all_blocks
    
    def get_block(self, document_id: str, block_id: str) -> Dict[str, Any]:
        """
        获取单个块信息
        
        Args:
            document_id: 文档 ID
            block_id: 块 ID
        
        Returns:
            块信息字典
        """
        endpoint = f"/docx/v1/documents/{document_id}/blocks/{block_id}"
        return self._request("GET", endpoint)
    
    def create_block_children(self, document_id: str, block_id: str, children: List[Dict]) -> Dict[str, Any]:
        """
        在指定块下创建子块
        
        Args:
            document_id: 文档 ID
            block_id: 父块 ID
            children: 子块列表
        
        Returns:
            创建结果
        """
        endpoint = f"/docx/v1/documents/{document_id}/blocks/{block_id}/children"
        body = {"children": children}
        return self._request("POST", endpoint, json=body)
    
    def update_block(self, document_id: str, block_id: str, update_data: Dict) -> Dict[str, Any]:
        """
        更新块内容
        
        Args:
            document_id: 文档 ID
            block_id: 块 ID
            update_data: 更新数据
        
        Returns:
            更新结果
        """
        endpoint = f"/docx/v1/documents/{document_id}/blocks/{block_id}"
        return self._request("PATCH", endpoint, json=update_data)
    
    def batch_update_blocks(self, document_id: str, requests_list: List[Dict]) -> Dict[str, Any]:
        """
        批量更新块
        
        Args:
            document_id: 文档 ID
            requests_list: 更新请求列表
        
        Returns:
            批量更新结果
        """
        endpoint = f"/docx/v1/documents/{document_id}/blocks/batch_update"
        body = {"requests": requests_list}
        return self._request("PATCH", endpoint, json=body)
    
    def delete_block_children(self, document_id: str, block_id: str, start_index: int, end_index: int) -> Dict[str, Any]:
        """
        删除指定范围的子块
        
        Args:
            document_id: 文档 ID
            block_id: 父块 ID
            start_index: 开始索引
            end_index: 结束索引
        
        Returns:
            删除结果
        """
        endpoint = f"/docx/v1/documents/{document_id}/blocks/{block_id}/children/batch_delete"
        body = {
            "start_index": start_index,
            "end_index": end_index
        }
        return self._request("DELETE", endpoint, json=body)


# ============ 工具函数 ============

def create_text_element(text: str, styles: Dict = None) -> Dict:
    """
    创建文本元素
    
    Args:
        text: 文本内容
        styles: 样式字典（如加粗、斜体等）
    
    Returns:
        文本元素字典
    """
    element = {
        "type": "text",
        "text": text
    }
    if styles:
        element["text_element_style"] = styles
    return element


def create_text_block(content: str, block_type: int = 2) -> Dict:
    """
    创建文本块
    
    Args:
        content: 文本内容
        block_type: 块类型（默认 2 为普通文本）
    
    Returns:
        块字典
    """
    return {
        "block_type": block_type,
        "text": {
            "elements": [create_text_element(content)]
        }
    }


def create_heading_block(content: str, level: int = 1) -> Dict:
    """
    创建标题块
    
    Args:
        content: 标题内容
        level: 标题级别（1-3）
    
    Returns:
        块字典
    """
    block_types = {1: 3, 2: 4, 3: 5}  # 映射到 Feishu 块类型
    block_type = block_types.get(level, 3)
    
    return {
        "block_type": block_type,
        f"heading{level}": {
            "elements": [create_text_element(content)]
        }
    }


def create_bullet_block(content: str, checked: bool = None) -> Dict:
    """
    创建列表项（项目符号或待办事项）
    
    Args:
        content: 内容
        checked: 是否勾选（None 为普通项目符号，True/False 为待办事项）
    
    Returns:
        块字典
    """
    if checked is not None:
        # 待办事项
        return {
            "block_type": FeishuDocAPI.BLOCK_TYPE_TODO,
            "todo": {
                "elements": [create_text_element(content)],
                "checked": checked
            }
        }
    else:
        # 普通项目符号
        return {
            "block_type": FeishuDocAPI.BLOCK_TYPE_BULLET,
            "bullet": {
                "elements": [create_text_element(content)]
            }
        }


def create_code_block(content: str, language: str = "plain") -> Dict:
    """
    创建代码块
    
    Args:
        content: 代码内容
        language: 编程语言
    
    Returns:
        块字典
    """
    return {
        "block_type": FeishuDocAPI.BLOCK_TYPE_CODE,
        "code": {
            "elements": [create_text_element(content)],
            "language": language
        }
    }


def create_divider_block() -> Dict:
    """创建分割线块"""
    return {
        "block_type": FeishuDocAPI.BLOCK_TYPE_DIVIDER,
        "divider": {}
    }


if __name__ == "__main__":
    # 测试基础功能
    print("=" * 50)
    print("测试飞书文档 API 基础功能")
    print("=" * 50)
    
    try:
        # 初始化客户端
        api = FeishuDocAPI()
        print("✅ 客户端初始化成功")
        print(f"   App ID: {api.app_id[:10]}...")
        
        # 获取 token
        token = api._get_tenant_access_token()
        print(f"✅ Token 获取成功: {token[:20]}...")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
