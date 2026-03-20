"""
飞书文档权限管理工具
支持添加、删除、查询文档权限
"""

import requests
import json
import sys

# 配置信息
FEISHU_CONFIG = {
    "app_id": "cli_a92ce0bd32781cb6",
    "app_secret": "pCao3DxI8w9QxVKx6I2nkdNLhdXle2u0",
}

BASE_URL = "https://open.feishu.cn/open-apis"


class FeishuPermissionManager:
    """飞书文档权限管理器"""
    
    def __init__(self):
        self.app_id = FEISHU_CONFIG["app_id"]
        self.app_secret = FEISHU_CONFIG["app_secret"]
        self.base_url = BASE_URL
        self._access_token = None
        
    def _get_access_token(self):
        """获取 tenant_access_token"""
        if self._access_token:
            return self._access_token
            
        url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
        resp = requests.post(url, json={
            "app_id": self.app_id,
            "app_secret": self.app_secret
        })
        
        data = resp.json()
        if data.get("code") != 0:
            raise Exception(f"获取 access_token 失败: {data.get('msg')}")
        
        self._access_token = data["tenant_access_token"]
        return self._access_token
    
    def _get_headers(self):
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json"
        }
    
    def add_permission(self, document_id, member_id, perm="full_access", need_notification=False):
        """
        添加协作者权限
        
        Args:
            document_id: 文档ID
            member_id: 用户 open_id
            perm: 权限类型
                - view: 可阅读
                - edit: 可编辑
                - full_access: 所有权限（可管理，包括删除）
            need_notification: 是否通知用户
        
        Returns:
            bool: 是否成功
        """
        url = f"{self.base_url}/drive/v1/permissions/{document_id}/members?type=docx&need_notification={str(need_notification).lower()}"
        headers = self._get_headers()
        data = {
            "member_type": "openid",
            "member_id": member_id,
            "perm": perm
        }
        
        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()
            if result.get("code") == 0:
                perm_names = {
                    "view": "可阅读",
                    "edit": "可编辑",
                    "full_access": "所有权限（可管理/删除）"
                }
                print(f"✅ 权限添加成功！")
                print(f"   用户: {member_id}")
                print(f"   权限: {perm_names.get(perm, perm)}")
                return True
            else:
                print(f"❌ 添加权限失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"❌ 添加权限错误: {e}")
            return False
    
    def remove_permission(self, document_id, member_id):
        """
        删除协作者权限
        
        Args:
            document_id: 文档ID
            member_id: 用户 open_id
        
        Returns:
            bool: 是否成功
        """
        url = f"{self.base_url}/drive/v1/permissions/{document_id}/members/{member_id}?type=docx&member_type=openid"
        headers = self._get_headers()
        
        try:
            resp = requests.delete(url, headers=headers)
            result = resp.json()
            if result.get("code") == 0:
                print(f"✅ 权限删除成功！")
                print(f"   用户: {member_id}")
                return True
            else:
                print(f"❌ 删除权限失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"❌ 删除权限错误: {e}")
            return False
    
    def get_permissions(self, document_id):
        """
        获取文档权限列表
        
        Args:
            document_id: 文档ID
        
        Returns:
            list: 权限列表
        """
        url = f"{self.base_url}/drive/v1/permissions/{document_id}/members?type=docx"
        headers = self._get_headers()
        
        try:
            resp = requests.get(url, headers=headers)
            result = resp.json()
            if result.get("code") == 0:
                members = result.get("data", {}).get("members", [])
                print(f"\n📋 文档权限列表（共 {len(members)} 人）：")
                print("-" * 60)
                
                perm_names = {
                    "view": "可阅读",
                    "edit": "可编辑",
                    "full_access": "所有权限"
                }
                
                for member in members:
                    member_type = member.get("member_type", "N/A")
                    member_id = member.get("member_id", "N/A")
                    perm = member.get("perm", "N/A")
                    perm_name = perm_names.get(perm, perm)
                    
                    print(f"   类型: {member_type}")
                    print(f"   ID: {member_id}")
                    print(f"   权限: {perm_name}")
                    print("-" * 60)
                
                return members
            else:
                print(f"❌ 获取权限列表失败: {result.get('msg')}")
                return []
        except Exception as e:
            print(f"❌ 获取权限列表错误: {e}")
            return []
    
    def transfer_ownership(self, document_id, new_owner_id):
        """
        转移文档所有权
        
        Args:
            document_id: 文档ID
            new_owner_id: 新所有者 open_id
        
        Returns:
            bool: 是否成功
        """
        url = f"{self.base_url}/drive/v1/permissions/{document_id}/transfer?type=docx"
        headers = self._get_headers()
        data = {
            "owner_type": "openid",
            "owner_id": new_owner_id
        }
        
        try:
            resp = requests.post(url, headers=headers, json=data)
            result = resp.json()
            if result.get("code") == 0:
                print(f"✅ 所有权转移成功！")
                print(f"   新所有者: {new_owner_id}")
                return True
            else:
                print(f"❌ 转移所有权失败: {result.get('msg')}")
                return False
        except Exception as e:
            print(f"❌ 转移所有权错误: {e}")
            return False


def print_usage():
    """打印使用说明"""
    print("=" * 70)
    print("📋 飞书文档权限管理工具")
    print("=" * 70)
    print("\n使用方法：")
    print("\n1. 添加权限（最高权限 - 可管理/删除）：")
    print("   python permission_manager.py add <document_id> <user_open_id>")
    print("\n2. 添加权限（可编辑）：")
    print("   python permission_manager.py add <document_id> <user_open_id> edit")
    print("\n3. 添加权限（仅可阅读）：")
    print("   python permission_manager.py add <document_id> <user_open_id> view")
    print("\n4. 删除权限：")
    print("   python permission_manager.py remove <document_id> <user_open_id>")
    print("\n5. 查看权限列表：")
    print("   python permission_manager.py list <document_id>")
    print("\n6. 转移所有权：")
    print("   python permission_manager.py transfer <document_id> <new_owner_open_id>")
    print("\n权限说明：")
    print("   - view: 可阅读")
    print("   - edit: 可编辑")
    print("   - full_access: 所有权限（可管理、可删除）")
    print("=" * 70)


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print_usage()
        return
    
    command = sys.argv[1]
    manager = FeishuPermissionManager()
    
    if command == "add":
        if len(sys.argv) < 4:
            print("❌ 参数不足")
            print("用法: python permission_manager.py add <document_id> <user_open_id> [perm]")
            return
        
        document_id = sys.argv[2]
        user_id = sys.argv[3]
        perm = sys.argv[4] if len(sys.argv) > 4 else "full_access"
        
        print("=" * 70)
        print("🔐 添加文档权限")
        print("=" * 70)
        print(f"\n📄 文档 ID: {document_id}")
        print(f"👤 用户 ID: {user_id}")
        print(f"🔑 权限类型: {perm}")
        print()
        
        manager.add_permission(document_id, user_id, perm)
    
    elif command == "remove":
        if len(sys.argv) < 4:
            print("❌ 参数不足")
            print("用法: python permission_manager.py remove <document_id> <user_open_id>")
            return
        
        document_id = sys.argv[2]
        user_id = sys.argv[3]
        
        print("=" * 70)
        print("🗑️  删除文档权限")
        print("=" * 70)
        print(f"\n📄 文档 ID: {document_id}")
        print(f"👤 用户 ID: {user_id}")
        print()
        
        manager.remove_permission(document_id, user_id)
    
    elif command == "list":
        if len(sys.argv) < 3:
            print("❌ 参数不足")
            print("用法: python permission_manager.py list <document_id>")
            return
        
        document_id = sys.argv[2]
        
        print("=" * 70)
        print("📋 查看文档权限")
        print("=" * 70)
        print(f"\n📄 文档 ID: {document_id}")
        
        manager.get_permissions(document_id)
    
    elif command == "transfer":
        if len(sys.argv) < 4:
            print("❌ 参数不足")
            print("用法: python permission_manager.py transfer <document_id> <new_owner_open_id>")
            return
        
        document_id = sys.argv[2]
        new_owner_id = sys.argv[3]
        
        print("=" * 70)
        print("🔄 转移文档所有权")
        print("=" * 70)
        print(f"\n📄 文档 ID: {document_id}")
        print(f"👤 新所有者: {new_owner_id}")
        print()
        
        manager.transfer_ownership(document_id, new_owner_id)
    
    else:
        print(f"❌ 未知命令: {command}")
        print_usage()


if __name__ == "__main__":
    main()
