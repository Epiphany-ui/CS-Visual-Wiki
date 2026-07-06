#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI 接口服务模块
功能：封装Manim动画AI引擎能力，提供标准化HTTP接口供外部调用
依赖：fastapi, uvicorn, pydantic, ai_engine
创建日期：2026/7/6
"""
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
import uvicorn
from typing import Optional

# 导入核心AI引擎流水线
from ai_engine import run_full_pipeline

# ===================== 服务配置常量 =====================
SERVER_HOST: str = "0.0.0.0"
SERVER_PORT: int = 8000
# 默认最大重试次数
DEFAULT_MAX_RETRY: int = 3

# ===================== FastAPI 应用初始化 =====================
app = FastAPI(
    title="Manim动画自动生成引擎API",
    description="基于本地大模型的Manim动画自动生成服务，支持RAG检索、代码生成、自动调试修复全流程",
    version="1.0.0"
)


# ===================== 请求体模型 =====================
class GenerateRequest(BaseModel):
    """
    动画生成接口请求体模型
    """
    user_input: str = Field(..., description="用户自然语言动画需求，必填项")
    max_retry: Optional[int] = Field(DEFAULT_MAX_RETRY, description="最大失败重试次数，选填，默认3次")


# ===================== 健康检查接口 =====================
@app.get("/health", summary="服务健康检查")
def health_check():
    """
    健康检查接口，用于服务探活与状态监控
    :return: 服务状态信息
    """
    return {
        "status": "ok",
        "service": "manim-animation-engine",
        "version": "1.0.0"
    }


# ===================== 核心生成接口 =====================
@app.post("/generate", summary="Manim动画生成（自动生成+调试修复）")
def generate_animation(request: GenerateRequest):
    """
    根据用户自然语言需求，执行完整流水线生成Manim动画视频
    流程：RAG检索 -> 代码生成 -> 渲染校验 -> 失败自动修复重试
    :param request: 生成请求参数
    :return: 标准化结果，包含成功状态、代码、视频路径、重试次数、日志
    """
    # 空输入校验：去除首尾空白后判断，避免纯空格无效请求
    if not request.user_input or not request.user_input.strip():
        raise HTTPException(
            status_code=400,
            detail="user_input 不能为空，请输入有效的动画描述需求"
        )

    try:
        # 调用核心AI引擎流水线
        pipeline_result = run_full_pipeline(
            user_requirement=request.user_input.strip(),
            max_retry=request.max_retry
        )
        return pipeline_result

    except HTTPException:
        # 主动抛出的HTTP异常直接透传
        raise
    except Exception as e:
        # 业务异常捕获，返回500错误
        raise HTTPException(
            status_code=500,
            detail=f"动画生成服务内部错误：{str(e)}"
        )


# ===================== 全局异常兜底处理器 =====================
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常捕获兜底，保证所有异常都返回标准格式响应，避免服务直接崩溃
    :param request: 请求对象
    :param exc: 异常实例
    :return: 标准化错误结果
    """
    return {
        "success": False,
        "code": "",
        "video_path": "",
        "try_count": 0,
        "log": f"服务全局异常：{str(exc)}"
    }


# ===================== 服务启动入口 =====================
if __name__ == "__main__":
    # 启动Uvicorn服务，支持直接运行 python main.py
    uvicorn.run(
        app="main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=False,
        log_level="info"
    )