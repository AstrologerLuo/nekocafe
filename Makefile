.PHONY: up down test lint build clean help

## 一键启动本地完整栈（含 build）
up:
	docker compose up -d --build

## 停止并清理容器与 volumes
down:
	docker compose down -v

## 运行预约服务单元测试（含覆盖率报告）
test:
	docker compose exec reservation pytest tests/ -v --cov=src --cov-report=term-missing

## 运行 lint 检查（Python: ruff; Node: eslint）
lint:
	docker compose run --rm reservation ruff check src/ tests/
	docker compose run --rm member npx eslint src/

## 本地构建所有镜像（不启动）
build:
	docker compose build

## 清理所有本地镜像
clean:
	docker compose down -v --rmi local

## 查看健康状态
health:
	@echo "=== 预约服务 ===" && curl -sf http://localhost:8081/healthz || echo "DOWN"
	@echo "=== 会员服务 ===" && curl -sf http://localhost:8082/healthz || echo "DOWN"
	@echo "=== API 网关 ===" && curl -sf http://localhost:8080/ || echo "DOWN"

## 查看所有可用命令
help:
	@grep -E '^##' $(MAKEFILE_LIST) | sed 's/## //'
