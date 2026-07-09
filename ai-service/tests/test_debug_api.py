#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试逐帧调试 API"""
import pytest
import os


class TestDebugAPI:
    """逐帧调试端点测试"""

    def test_video_info_nonexistent(self, client):
        """GET /api/debug/video/xxx/info 对不存在的视频返回错误"""
        response = client.get("/api/debug/video/nonexistent.mp4/info")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0

    def test_frames_blocked_path_traversal(self, client):
        """逐帧端点阻止路径穿越——FastAPI 自动规范化路径返回 404"""
        response = client.get("/api/debug/video/../../../etc/passwd/info")
        # FastAPI/Starlette 将 ../ 规范化后路径不匹配任何路由，返回 404
        assert response.status_code == 404

    def test_frames_nonexistent_video(self, client):
        """对不存在的视频提取帧返回错误"""
        response = client.get("/api/debug/video/fake.mp4/frames?start_frame=0&end_frame=5")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0

    def test_single_frame_nonexistent(self, client):
        """对不存在的帧返回错误"""
        response = client.get("/api/debug/video/fake.mp4/frame/0")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0

    def test_frame_at_time_rejects_path_traversal(self, client):
        """时间点截图的路径穿越被 FastAPI 自动规范化返回 404"""
        response = client.get("/api/debug/video/../secret.mp4/frame-at-time?time=1.0")
        # FastAPI/Starlette 将 ../ 规范化后路由不匹配，返回 404
        assert response.status_code == 404

    def test_thumbnail_sheet_blocked_path(self, client):
        """缩略图端点阻止路径穿越"""
        response = client.get("/api/debug/video/..\\..\\secret.mp4/thumbnail-sheet")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] != 0
