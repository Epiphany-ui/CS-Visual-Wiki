# CS-Visual-Learn AI Service Dockerfile
# 基于 Python 3.10，包含 Manim + FastAPI + Celery
FROM python:3.10-slim

LABEL description="CS-Visual-Learn AI Engine Service"
LABEL version="0.2.0"

# 系统依赖：ffmpeg（Manim 渲染）、LaTeX（数学公式）
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-science \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存层
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建运行时目录
RUN mkdir -p outputs/code outputs/videos media cache logs

# 暴露端口
EXPOSE 8000

# 默认启动 API 服务
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
