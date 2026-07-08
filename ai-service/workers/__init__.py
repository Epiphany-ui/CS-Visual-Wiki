# Celery异步任务包
import sys
from pathlib import Path

# 确保 ai-service 目录在 sys.path 中（必须在导入 celery_app 之前执行，
# 因为 celery_app 内部有 from ai_engine import ... 的顶层绝对导入）
_AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
if str(_AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SERVICE_DIR))

from .celery_app import celery_app

__all__ = ['celery_app']
