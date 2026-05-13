#!/usr/bin/env bash
# health-check.sh - 本地环境健康检查脚本
set -euo pipefail

BASE_URL="${1:-http://localhost}"
PASS=0
FAIL=0

check() {
  local name="$1"
  local url="$2"
  local expected="${3:-200}"
  if curl -sf -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected"; then
    echo "✅ $name: OK ($url)"
    PASS=$((PASS+1))
  else
    echo "❌ $name: FAIL ($url)"
    FAIL=$((FAIL+1))
  fi
}

echo "=== NekoCafé 健康检查 ==="
check "API 网关"    "${BASE_URL}:8080/healthz"
check "预约服务"   "${BASE_URL}:8081/healthz"
check "会员服务"   "${BASE_URL}:8082/healthz"
check "Grafana"    "${BASE_URL}:3000/api/health"
check "Prometheus" "${BASE_URL}:9090/-/healthy"

echo ""
echo "=== 结果：PASS=$PASS FAIL=$FAIL ==="
[ $FAIL -eq 0 ] && exit 0 || exit 1
