#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pygmalion DiffuServo V4 主程序
"""
from core import DiffuServoV4

if __name__ == "__main__":
    try:
        bot = DiffuServoV4()
        bot.run()
    except Exception as e:
        print(f"❌ 程序运行时发生严重错误: {e}")
        import traceback
        traceback.print_exc()
