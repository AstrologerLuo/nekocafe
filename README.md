# NekoCafé

> NekoCafé 猫咪主题餐饮预约平台 — 实验三 DevOps PoC 仓库

## 项目简介

本仓库为 NekoCafé 平台的 DevOps PoC（概念验证）代码仓库，覆盖**预约服务**与**会员服务**两个核心微服务的完整 CI/CD 流水线与容器化部署方案。

- 班级 / 学号 / 姓名：计算机23-3班 / 220902105 / 罗星宇
- 案例项目：NekoCafé 猫咪主题餐饮预约平台（12城 38门店）
- 文档版本：v1.1 · 2026-05-15

---

## 仓库结构说明

本仓库采用 **Monorepo** 结构，将两个服务、CI/CD 配置、运维文档统一管理。

### Monorepo vs Polyrepo 取舍

| 维度 | Monorepo（本方案）| Polyrepo |
|------|-------------------|----------|
| 代码共享 | 方便共享工具库/类型定义 | 需要发布 npm/pypi 包 |
| CI/CD | 单一流水线配置，路径过滤触发 | 各仓库独立流水线 |
| 版本一致性 | 统一锁文件，依赖版本一致 | 可能版本漂移 |
| 权限管理 | CODEOWNERS 精细控制 | 仓库级权限更简单 |
| 适用阶段 | PoC / 小团队迭代 | 大规模多团队 |

**决策**：PoC 阶段选择 Monorepo，方便统一管理。待服务数量超过 5 个或团队超过 10 人时再评估拆分。

---

## 目录结构

```
nekocafe/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml              # CI 流水线（lint/test/scan/build）
│   │   └── cd.yml              # CD 流水线（dev/staging/prod 部署）
│   └── CODEOWNERS              # 代码负责人配置
├── services/
│   ├── reservation/            # 预约服务（Python 3.12 / FastAPI）
│   │   ├── src/
│   │   │   ├── __init__.py
│   │   │   ├── main.py         # FastAPI 应用入口
│   │   │   ├── models.py       # 数据模型
│   │   │   ├── routers/        # 路由模块
│   │   │   └── telemetry.py    # OpenTelemetry 集成（HTTP OTLP）
│   │   ├── tests/
│   │   │   ├── conftest.py     # pytest 路径配置
│   │   │   ├── test_smoke.py   # 冒烟测试
│   │   │   └── test_reservation.py  # 业务单元测试
│   │   ├── Dockerfile          # 多阶段构建（非 root 运行）
│   │   ├── requirements.txt    # 生产依赖
│   │   └── requirements-dev.txt # 开发依赖
│   ├── member/                 # 会员服务（Node.js 20 / Express）
│   │   ├── src/
│   │   │   ├── index.js        # Express 应用入口
│   │   │   ├── routes/         # 路由模块
│   │   │   └── telemetry.js    # OpenTelemetry 集成（HTTP OTLP）
│   │   ├── Dockerfile          # 多阶段构建（npm 国内镜像加速）
│   │   ├── package.json
│   │   └── package-lock.json
│   ├── prometheus/             # Prometheus 配置
│   │   └── prometheus.yml       # scrape targets 配置
│   ├── grafana/                # Grafana 配置
│   │   └── provisioning/
│   │       ├── datasources/     # 自动配置数据源
│   │       └── dashboards/      # NekoCafé 专属仪表盘
│   ├── otelcol/                 # OpenTelemetry Collector 配置
│   │   └── config.yaml          # 接收/转发 OTLP → Prometheus/Loki/Tempo
│   └── tempo/                   # Tempo 链路追踪配置
│       └── tempo.yaml           # Jaeger/OTLP 接收，local 存储
├── docker-compose.yml           # 本地一键起栈（含可观测性全家桶）
├── docker-compose.override.yml # 本地开发覆盖配置
├── .editorconfig               # 编辑器配置
├── .pre-commit-config.yaml     # pre-commit 钩子
├── Makefile                    # 常用命令快捷方式
└── README.md
```

---

## 快速开始

### 前置要求

- Docker Desktop >= 24.0
- Docker Compose >= 2.20
- Make（可选，Windows 可直接执行等价命令）

### 一键启动（本地开发）

```bash
# 克隆仓库
git clone https://github.com/AstrologerLuo/nekocafe.git
cd nekocafe

# 一键启动完整栈（含 PostgreSQL + Redis + 两个服务）
make up
# 等价于：docker compose up -d --build

# 验证服务健康
curl http://localhost:8081/healthz   # 预约服务
curl http://localhost:8082/healthz   # 会员服务
curl http://localhost:8080/          # API 网关
```

### 运行测试

```bash
make test
# 等价于：docker compose exec reservation pytest tests/ -v --cov=src --cov-report=term-missing
```

### 停止并清理

```bash
make down
# 等价于：docker compose down -v
```

---

## 环境说明

| 环境 | 触发条件 | 部署方式 | 说明 |
|------|----------|----------|------|
| **dev** | `main` 分支 push/merge | GitHub Actions 自动部署 | 金丝雀发布（5%→25%→100%）|
| **staging** | 打 `v*.*.*-staging` tag | 需要手动审批 | 金丝雀发布 |
| **prod** | 打 `v*.*.*` tag | 需要手动审批 | 蓝绿部署 |

---

## CI/CD 流水线

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CI 流水线                                   │
│                                                                         │
│  Lint ──┬── Unit Test ── Build & Scan ── Integration Test ── Push GHCR │
│  ruff   │  pytest+Jest   Docker+Trivy      docker compose    GHCR 推送  │
│  eslint └── SAST                                                       │
│              bandit+npm audit                                           │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              CD 流水线                                   │
│                                                                         │
│  [CD] 自动/手动部署 → 金丝雀/蓝绿发布 → 监控检测                        │
│                      → 自动回滚（P95>500ms 或错误率>1%）                 │
└─────────────────────────────────────────────────────────────────────────┘
```

| 阶段 | 工具 | 说明 |
|------|------|------|
| Lint | ruff / eslint | 代码格式与质量 |
| SAST | bandit / npm audit | 静态应用安全测试 |
| Unit Test | pytest / Jest | 单元测试 + 覆盖率 |
| Build & Scan | Docker Buildx + Trivy | 多阶段构建 + 容器漏洞扫描 |
| Integration Test | docker compose | 全栈启动 + 冒烟测试 |
| Push GHCR | build-push-action | 推送镜像至 GitHub Container Registry |

详见 `.github/workflows/ci.yml` 和 `.github/workflows/cd.yml`。

---

## 可观测性

本项目集成了完整的可观测性技术栈（Metrics + Logs + Traces），基于 **OpenTelemetry** 标准。

### 架构概览

```
┌──────────────┐    OTLP/HTTP     ┌─────────────────┐
│  reservation │ ───(4318)────────▶                 │
│   (Python)   │                  │  OpenTelemetry  │
└──────────────┘    OTLP/HTTP     │    Collector    │
┌──────────────┐ ───(4318)────────▶                 │──▶ Prometheus (9090)
│    member    │                  │  (otelcol)      │──▶ Loki (3100)
│  (Node.js)  │                  └─────────────────┘──▶ Tempo (4317/3200)
└──────────────┘
```

### 组件说明

| 组件 | 用途 | 端口 | 访问地址 |
|------|------|------|----------|
| Prometheus | 指标采集（CPU/内存/请求率/延迟） | 9090 | http://localhost:9090 |
| Grafana | 可视化 Dashboard | 3000 | http://localhost:3000 （admin/admin） |
| Loki | 日志聚合（服务日志） | 3100 | 集成于 Grafana |
| Tempo | 分布式链路追踪 | 3200 (HTTP) / 4317 (gRPC) | 集成于 Grafana |
| OTEL Collector | 统一收集转发 | 4317 (gRPC) / 4318 (HTTP) | 自动接收并路由 |

### Grafana 仪表盘

一键启动后，Grafana 会自动加载 **NekoCafé 服务监控** 仪表盘，包含以下面板：

- 服务健康状态（在线/离线）
- 请求速率（req/s）
- 响应延迟（P50 / P95 / P99）
- 5xx 错误率
- 内存使用量
- 服务日志（Loki 面板）

访问路径：`Grafana → Dashboards → NekoCafé 服务监控`

### 查看日志

在 Grafana 中切换到 **Explore** 页面：
1. 选择 **Loki** 数据源
2. 输入 `{"service_name": "reservation"}` 或 `{"service_name": "member"}` 过滤日志
3. 点击 **Run query** 查看实时日志流

### 查看链路追踪

在 Grafana 中切换到 **Explore** 页面：
1. 选择 **Tempo** 数据源
2. 输入 Trace ID 或按服务名过滤
3. 点击 **Run query** 查看完整调用链

### Prometheus 指标端点

| 服务 | 指标路径 |
|------|----------|
| reservation | http://localhost:8081/metrics |
| member | http://localhost:8082/metrics |
| otelcol | http://localhost:8889/metrics |

---

## 安全合规

- **Secret 管理**：所有密钥通过 GitHub Secrets 注入，禁止硬编码
- **镜像扫描**：Trivy 扫描无 HIGH/CRITICAL 漏洞方可推送
- **非 root 运行**：所有容器以 `app` 用户运行
- **IaC Linter**：hadolint / kube-linter / yamllint 集成于 CI

---

## 参考文档

- [运维手册](./docs/runbook.md)
- [回滚手册](./docs/rollback.md)
