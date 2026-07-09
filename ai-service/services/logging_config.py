#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一日志配置
为 ai-service 所有模块提供一致的日志格式和输出方式。
替换各模块中散落的 print() 调用，支持控制台 + 文件双输出。
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler

# 日志目录
LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_FILE = LOG_DIR / "ai-service.log"

# 日志格式
CONSOLE_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
FILE_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(level: int = logging.INFO, enable_file: bool = True):
    """初始化全局日志配置（幂等，只执行一次）"""
    root = logging.getLogger("ai_service")
    if root.handlers:
        return root  # 已初始化

    root.setLevel(level)

    # 控制台输出
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(CONSOLE_FORMAT, datefmt=DATE_FORMAT))
    root.addHandler(console)

    # 文件输出（带轮转，单文件最大 10MB，保留 3 个备份）
    if enable_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            str(LOG_FILE), maxBytes=10 * 1024 * 1024, backupCount=3, encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(FILE_FORMAT, datefmt=DATE_FORMAT))
        root.addHandler(file_handler)

    return root


def get_logger(name: str) -> logging.Logger:
    """获取模块级 logger（自动继承根配置）"""
    return logging.getLogger(f"ai_service.{name}")
