# syntax=docker/dockerfile:1.9
# =========================================================
# NekoCafé 预约服务 - 多阶段 Dockerfile
# 目标：最终镜像 ≤ 200 MB，非 root 运行，通过 Trivy 扫描
# =========================================================

# ---- 阶段1：构建依赖 ----
FROM python:3.12-slim AS builder

WORKDIR /app

# 仅复制依赖文件，利用 Docker Layer Cache
COPY requirements.txt .

# --no-cache-dir 减小体积；pip wheel 提前编译
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

# ---- 阶段2：最终运行镜像 ----
FROM python:3.12-slim AS runtime

# 安全加固：创建非 root 用户
RUN groupadd --gid 1001 app \
    && useradd --uid 1001 --gid 1001 --no-create-home app

WORKDIR /app

# 仅从 builder 复制已安装的包和应用代码
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src ./src

# 切换到非 root 用户
USER app

# 声明端口
EXPOSE 8080

# 健康检查（镜像内自带）
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/healthz')" || exit 1

# 启动命令
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
