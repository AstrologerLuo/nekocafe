# Runbook - NekoCafé 预约/会员服务运维手册

> 版本：v1.0 · 2026-05-13 · 负责人：罗星宇

---

## 1. 服务概览

| 服务 | 端口 | 技术栈 | 健康检查端点 |
|------|------|--------|-------------|
| 预约服务 | 8081 | Python 3.12 / FastAPI | `/healthz` |
| 会员服务 | 8082 | Node.js 20 / Express | `/healthz` |
| API 网关 | 8080 | Nginx 1.25 | `/healthz` |
| PostgreSQL | 5432 | PostgreSQL 16 | `pg_isready` |
| Redis | 6379 | Redis 7 | `redis-cli ping` |

---

## 2. 告警处理流程

### 2.1 服务 P99 延迟超阈值（> 800ms）

1. 打开 Grafana → Dashboard → NekoCafé Overview → P99 延迟面板
2. 确认是哪个服务/端点的延迟上升（通过 `service` label 过滤）
3. 在 Loki 检索最近 5 分钟的 ERROR 日志：
   ```logql
   {service="reservation-svc"} |= "ERROR" | json | line_format "{{.message}}"
   ```
4. 在 Tempo 中找出高延迟的 traceId，点击查看链路详情
5. 判断原因：
   - DB 慢查询 → 检查 PostgreSQL 慢日志，必要时 EXPLAIN ANALYZE
   - 下游服务超时 → 检查依赖服务健康状态
   - 代码 Bug → 查看 Error 日志，若需要则触发回滚

### 2.2 服务 5xx 错误率 > 1%

1. 在 Grafana 确认错误率面板，识别 affected 服务
2. 检查 Pod 状态：
   ```bash
   kubectl get pods -n nekocafe-prod -l app=reservation
   kubectl describe pod <pod-name> -n nekocafe-prod
   ```
3. 查看 Pod 最近日志：
   ```bash
   kubectl logs <pod-name> -n nekocafe-prod --tail=100 -f
   ```
4. 若 Pod 处于 CrashLoopBackOff，立即执行回滚（见 [rollback.md](./rollback.md)）
5. 否则尝试重启 Pod：
   ```bash
   kubectl rollout restart deployment/nekocafe-reservation -n nekocafe-prod
   ```

### 2.3 Pod 内存使用 > 512MB

1. 确认是内存泄漏还是流量突增
2. 临时扩容：
   ```bash
   kubectl scale deployment/nekocafe-reservation -n nekocafe-prod --replicas=3
   ```
3. 若 HPA 已启用，检查 HPA 状态：
   ```bash
   kubectl get hpa -n nekocafe-prod
   ```

---

## 3. 数据库维护

### 3.1 检查连接池状态

```sql
SELECT count(*), state FROM pg_stat_activity
WHERE datname = 'nekocafe_prod'
GROUP BY state;
```

### 3.2 查看慢查询

```sql
SELECT pid, now() - pg_stat_activity.query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND query_start < now() - interval '5 seconds'
ORDER BY duration DESC;
```

---

## 4. 紧急联系

| 角色 | 联系方式 |
|------|---------|
| 服务负责人 | 罗星宇（微信/飞书） |
| DBA | TODO |
| 运维负责人 | TODO |

---

## 5. 常用命令速查

```bash
# 查看所有 Pod 状态
kubectl get pods -n nekocafe-prod

# 查看服务日志（最近 100 行）
kubectl logs -n nekocafe-prod -l app=reservation --tail=100

# 强制重启 Deployment
kubectl rollout restart deployment/nekocafe-reservation -n nekocafe-prod

# 查看 Deployment 滚动更新状态
kubectl rollout status deployment/nekocafe-reservation -n nekocafe-prod

# 端口转发本地调试
kubectl port-forward svc/nekocafe-reservation 18081:8080 -n nekocafe-prod
```
