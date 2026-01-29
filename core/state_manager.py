#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pygmalion 状态管理系统
持久化生成状态，支持页面刷新恢复
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class GenerationStateManager:
    """生成状态管理器 - 支持持久化和恢复"""
    
    def __init__(self, state_dir: str = "./generation_state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        self.current_session: Optional[Dict] = None
        self.session_file: Optional[Path] = None
    
    def create_session(self, theme: str, target_score: float, max_iterations: int, 
                      quick_mode: bool) -> str:
        """创建新的生成会话"""
        session_id = f"gen_{int(time.time() * 1000)}"
        
        self.current_session = {
            "session_id": session_id,
            "theme": theme,
            "target_score": target_score,
            "max_iterations": max_iterations,
            "quick_mode": quick_mode,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "running",
            "iterations": [],
            "best_score": 0.0,
            "best_image": None,
            "completed_at": None
        }
        
        self.session_file = self.state_dir / f"{session_id}.json"
        self._save_session()
        
        logger.info(f"✅ 新会话创建: {session_id} (主题: {theme})")
        return session_id
    
    def add_iteration(self, iteration_num: int, image_path: str, score: float, 
                     model: str, prompt: str):
        """添加一次迭代的结果"""
        if not self.current_session:
            return
        
        iteration = {
            "iteration": iteration_num,
            "image_path": image_path,
            "score": score,
            "model": model,
            "prompt": prompt,
            "timestamp": datetime.now().isoformat()
        }
        
        self.current_session["iterations"].append(iteration)
        
        # 更新最优分数和图片
        if score > self.current_session["best_score"]:
            self.current_session["best_score"] = score
            self.current_session["best_image"] = image_path
        
        self.current_session["updated_at"] = datetime.now().isoformat()
        self._save_session()
        
        logger.debug(f"📝 迭代 {iteration_num} 保存: 分数={score:.2f}, 模型={model}")
    
    def complete_session(self):
        """标记会话为完成"""
        if not self.current_session:
            return
        
        self.current_session["status"] = "completed"
        self.current_session["completed_at"] = datetime.now().isoformat()
        self._save_session()
        
        logger.info(f"✅ 会话完成: {self.current_session['session_id']}")
    
    def fail_session(self, error: str):
        """标记会话为失败"""
        if not self.current_session:
            return
        
        self.current_session["status"] = "failed"
        self.current_session["error"] = error
        self.current_session["completed_at"] = datetime.now().isoformat()
        self._save_session()
        
        logger.error(f"❌ 会话失败: {self.current_session['session_id']} - {error}")
    
    def _save_session(self):
        """保存当前会话到文件"""
        if not self.current_session or not self.session_file:
            return
        
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_session, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ 保存会话失败: {e}")
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """获取指定会话的信息"""
        session_file = self.state_dir / f"{session_id}.json"
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ 读取会话失败: {e}")
            return None
    
    def list_sessions(self, limit: int = 10) -> List[Dict]:
        """列出最近的会话"""
        sessions = []
        
        # 获取所有会话文件
        for session_file in sorted(self.state_dir.glob("gen_*.json"), 
                                   key=lambda p: p.stat().st_mtime, 
                                   reverse=True)[:limit]:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session = json.load(f)
                    sessions.append({
                        "session_id": session["session_id"],
                        "theme": session["theme"],
                        "status": session["status"],
                        "best_score": session["best_score"],
                        "best_image": session["best_image"],
                        "iterations": len(session["iterations"]),
                        "created_at": session["created_at"],
                        "completed_at": session.get("completed_at")
                    })
            except Exception as e:
                logger.error(f"❌ 读取会话文件失败: {e}")
        
        return sessions
    
    def get_latest_session(self) -> Optional[Dict]:
        """获取最新的会话"""
        sessions = self.list_sessions(limit=1)
        if sessions:
            return self.get_session(sessions[0]["session_id"])
        return None
    
    def cleanup_old_sessions(self, days: int = 7):
        """清理旧会话文件"""
        import os
        cutoff_time = time.time() - (days * 86400)
        
        count = 0
        for session_file in self.state_dir.glob("gen_*.json"):
            if os.path.stat(session_file).st_mtime < cutoff_time:
                try:
                    session_file.unlink()
                    count += 1
                except Exception as e:
                    logger.error(f"❌ 删除会话文件失败: {e}")
        
        if count > 0:
            logger.info(f"🗑️ 清理了 {count} 个旧会话文件 (> {days} 天)")


# 全局状态管理器实例
state_manager = GenerationStateManager(state_dir="./generation_state")
