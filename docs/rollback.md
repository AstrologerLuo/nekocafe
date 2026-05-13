# Rollback - 回滚操作手册

> 版本：v1.0 · 2026-05-13 · 负责人：罗星宇

---

## 1. 自动回滚触发条件

以下任一条件满足时，Argo Rollouts 会自动触发回滚（无需人工干预）：

| 指标 | 阈值 | 监测窗口 |
|------|------|---------|
| P95 延迟 | > 500ms | 连续 5 分钟 |
| HTTP 5xx 错误率 | > 1% | 连续 3 分钟 |
| Pod CrashLoopBackOff | 连续 3 次重启 | 5 分钟内 |

---

## 2. 手动一键回滚

### 2.1 回滚预约服务（prod）

```bash
helm rollback nekocafe-reservation -n nekocafe-prod
```

### 2.2 回滚会员服务（prod）

```bash
helm rollback nekocafe-member -n nekocafe-prod
```

### 2.3 回滚指定版本（历史版本）

```bash
# 查看 Helm 发布历史
helm history nekocafe-reservation -n nekocafe-prod

# 回滚到指定版本（REVISION 为上一步查到的版本号）
helm rollback nekocafe-reservation <REVISION> -n nekocafe-prod
```

### 2.4 蓝绿回滚（仅 prod 环境）

若当前 prod 已切换到 green，需要紧急回切到 blue：

```bash
# 将 Service selector 切回 blue
kubectl patch svc nekocafe-reservation -n nekocafe-prod \
  -p '{"spec":{"selector":{"slot":"blue"}}}'

# 确认切换成功
kubectl get svc nekocafe-reservation -n nekocafe-prod -o jsonpath='{.spec.selector}'
```

---

## 3. 回滚后验证步骤

1. 检查服务健康状态：
   ```bash
   curl -sf https://nekocafe.example.com/healthz
   ```

2. 确认错误率恢复正常（Grafana → 错误率面板）

3. 在 Loki 中搜索回滚后的日志确认无异常：
   ```logql
   {service="reservation-svc"} |= "ERROR"
   ```

4. 通知相关人员：发送飞书消息，说明：
   - 回滚原因（附 traceId 或错误截图）
   - 回滚时间
   - 当前服务版本

---

## 4. 回滚后操作

- [ ] 提交 Post-Mortem 事故报告（在 GitHub Issues 中）
- [ ] 分析根本原因，修复 Bug 后重新走 CI/CD 流程上线
- [ ] 若涉及数据库变更，检查数据一致性

---

## 5. 注意事项

⚠️ **数据库回滚风险**：若新版本执行了不可逆的数据库迁移（如 DROP COLUMN），回滚代码版本可能导致数据不一致。此时须联系 DBA 进行数据库级别的回滚评估。

⚠️ **prod 回滚须通知**：prod 环境的任何回滚操作都必须在回滚前通知运维负责人，并在回滚完成后更新值班日志。
