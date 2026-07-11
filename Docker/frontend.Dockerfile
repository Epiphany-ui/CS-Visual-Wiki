# CS-Visual-Learn 前端 Dockerfile
# 多阶段构建：Node.js 编译 → Nginx 静态服务

# ==== 构建阶段 ====
FROM node:22-alpine AS build
WORKDIR /app

# 先复制依赖文件，利用缓存
COPY front-html/package*.json ./
RUN npm ci

# 复制源码并构建
COPY front-html/ .
RUN npm run build

# ==== 运行阶段 ====
FROM nginx:alpine
WORKDIR /usr/share/nginx/html

# 清除默认静态文件
RUN rm -rf ./*

# 复制构建产物
COPY --from=build /app/dist .

# 复制自定义 nginx 配置
COPY Docker/nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
