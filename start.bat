@echo off
title CS Visual Learn - Start All Services

set ROOT=%~dp0
set CONDA_ENV=E:\Anaconda\envs\manim_ai
set REDIS_EXE=C:\Program Files\Redis\redis-server.exe

echo ============================================
echo   CS Visual Learn - Starting Services...
echo ============================================
echo.

REM --- 1. Redis ---
echo [1/3] Starting Redis...
start "Redis" "%REDIS_EXE%"
timeout /t 2 /nobreak >nul
echo   Redis started (port 6379)
echo.

REM --- 2. FastAPI ---
echo [2/3] Starting API server (port 8000)...
cd /d "%ROOT%ai-service"
start "API-Server" cmd /c ""%CONDA_ENV%\python.exe" main.py"
echo   API server started (http://localhost:8000)
echo.

REM --- 3. Celery Worker ---
echo [3/3] Starting Celery Worker...
start "Celery-Worker" cmd /c ""%CONDA_ENV%\Scripts\celery.exe" -A workers.celery_app worker --loglevel=info -P solo"
echo   Celery Worker started
echo.

echo ============================================
echo   All services started!
echo   Redis:      localhost:6379
echo   API:        http://localhost:8000
echo   API Docs:   http://localhost:8000/docs
echo   Celery:     running in background
echo ============================================
echo.
echo Close each window to stop its service.
pause
