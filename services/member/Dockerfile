# syntax=docker/dockerfile:1.9
# =========================================================
# NekoCafé 会员服务 - 多阶段 Dockerfile
# 目标：最终镜像 ≤ 200 MB，非 root 运行，通过 Trivy 扫描
# =========================================================

# ---- 阶段1：安装依赖 ----
FROM node:20-alpine AS deps

WORKDIR /app

# 仅复制 package 文件，利用 Layer Cache
COPY package*.json ./

# 安装生产依赖（无 lockfile 时使用 install），使用国内镜像加速
RUN npm install --omit=dev --registry https://registry.npmmirror.com && npm cache clean --force

# ---- 阶段2：最终运行镜像 ----
FROM node:20-alpine AS runtime

# 安全加固：创建非 root 用户
RUN addgroup --gid 1001 app \
    && adduser --uid 1001 --ingroup app --disabled-password --no-create-home app

WORKDIR /app

# 仅从 deps 阶段复制 node_modules
COPY --from=deps --chown=app:app /app/node_modules ./node_modules

# 复制应用代码
COPY --chown=app:app src/ ./src/

# 切换到非 root 用户
USER app

EXPOSE 8080

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -qO- http://localhost:8080/healthz || exit 1

CMD ["node", "src/index.js"]
