#!/usr/bin/env python3
"""飞书机器人 - 最简单版本"""

import os
import json
import lark_oapi as lark
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")

# 获取需要用到的类
P2ImMessageReceiveV1 = getattr(lark.im.v1, 'P2ImMessageReceiveV1')
CreateMessageRequest = getattr(lark.im.v1, 'CreateMessageRequest')
CreateMessageRequestBody = getattr(lark.im.v1, 'CreateMessageRequestBody')


def reply_text(chat_id: str, text: str):
    """回复文本消息"""
    client = lark.Client.builder() \
        .app_id(APP_ID) \
        .app_secret(APP_SECRET) \
        .log_level(lark.LogLevel.INFO) \
        .build()
    
    req = CreateMessageRequest.builder() \
        .receive_id_type("chat_id") \
        .request_body(CreateMessageRequestBody.builder()
                      .receive_id(chat_id)
                      .msg_type("text")
                      .content(json.dumps({"text": text}))
                      .build()) \
        .build()
    
    resp = client.im.v1.message.create(req)
    if resp.success():
        print(f"[回复成功] {text[:50]}")
    else:
        print(f"[回复失败] {resp.code} {resp.msg}")


def on_message(data):
    """收到消息时的回调"""
    event = data.event
    message = event.message
    
    chat_id = message.chat_id
    msg_type = message.message_type
    content = message.content
    
    # 解析消息内容
    try:
        content_obj = json.loads(content)
        text = content_obj.get("text", "")
    except:
        text = str(content)
    
    print(f"[收到消息] chat_id={chat_id}, type={msg_type}, text={text}")
    
    # 排除机器人自己的消息
    if event.sender and event.sender.sender_type == "app":
        return
    
    # 回复消息
    reply_text(chat_id, f"收到: {text}")


def main():
    print("=" * 50)
    print("🤖 飞书机器人启动")
    print("=" * 50)
    
    # 创建事件处理器
    handler = lark.EventDispatcherHandler.builder("", "") \
        .register_p2_im_message_receive_v1(on_message) \
        .build()
    
    # 创建 WebSocket 客户端
    ws = lark.ws.Client(APP_ID, APP_SECRET, 
                        event_handler=handler,
                        log_level=lark.LogLevel.DEBUG)
    
    # 启动（阻塞）
    print("✅ 正在连接...")
    ws.start()


if __name__ == "__main__":
    main()
