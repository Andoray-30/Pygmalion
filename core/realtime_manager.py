#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pygmalion 实时推送服务
使用 Server-Sent Events 实现真正的实时推送
"""

import json
import asyncio
from typing import Set, Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RealtimeUpdateManager:
    """实时更新管理器 - 支持多客户端推送"""
    
    def __init__(self):
        self.subscribers: Dict[str, Set[asyncio.Queue]] = {}
        self.session_updates: Dict[str, List[Dict]] = {}
    
    def add_subscriber(self, session_id: str, queue: asyncio.Queue):
        """添加订阅者（客户端）"""
        if session_id not in self.subscribers:
            self.subscribers[session_id] = set()
            self.session_updates[session_id] = []
        
        self.subscribers[session_id].add(queue)
        logger.debug(f"✅ 订阅者已添加: {session_id} (当前: {len(self.subscribers[session_id])})")
    
    def remove_subscriber(self, session_id: str, queue: asyncio.Queue):
        """移除订阅者"""
        if session_id in self.subscribers:
            self.subscribers[session_id].discard(queue)
            if not self.subscribers[session_id]:
                del self.subscribers[session_id]
                logger.debug(f"🗑️ 会话已删除: {session_id}")
    
    async def broadcast_update(self, session_id: str, update_type: str, data: Dict):
        """广播更新到所有订阅者"""
        update = {
            "type": update_type,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        
        # 保存更新记录
        if session_id in self.session_updates:
            self.session_updates[session_id].append(update)
            # 只保存最近100条更新
            if len(self.session_updates[session_id]) > 100:
                self.session_updates[session_id].pop(0)
        
        # 推送给所有订阅者
        if session_id in self.subscribers:
            disconnected = set()
            for queue in self.subscribers[session_id]:
                try:
                    queue.put_nowait(update)
                except asyncio.QueueFull:
                    disconnected.add(queue)
            
            # 删除断开连接的客户端
            for queue in disconnected:
                self.remove_subscriber(session_id, queue)
            
            logger.debug(f"📤 广播更新 {session_id}: {update_type} (收件人: {len(self.subscribers[session_id])})")
    
    def get_session_updates(self, session_id: str) -> List[Dict]:
        """获取会话的所有更新（用于页面刷新时恢复）"""
        return self.session_updates.get(session_id, [])
    
    def clear_session_updates(self, session_id: str):
        """清空会话的更新记录"""
        if session_id in self.session_updates:
            self.session_updates[session_id] = []


# 全局实时更新管理器
realtime_manager = RealtimeUpdateManager()
