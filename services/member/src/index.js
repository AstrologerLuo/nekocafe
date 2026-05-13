/**
 * NekoCafé 会员服务入口
 * Express 应用，提供会员注册/登录、积分查询等接口
 */
'use strict';

const express = require('express');
const { setupTelemetry } = require('./telemetry');
const { healthRouter } = require('./routes/health');
const { memberRouter } = require('./routes/member');

// 初始化 OpenTelemetry（必须在其他模块之前调用）
setupTelemetry();

const app = express();
const PORT = process.env.PORT || 8080;

// ===== 中间件 =====
app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: false }));

// 结构化日志中间件
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const log = {
      timestamp: new Date().toISOString(),
      level: res.statusCode >= 500 ? 'ERROR' : 'INFO',
      service: 'member-svc',
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration_ms: Date.now() - start,
      trace_id: req.headers['x-trace-id'] || '',
    };
    process.stdout.write(JSON.stringify(log) + '\n');
  });
  next();
});

// ===== 路由 =====
app.use('/', healthRouter);
app.use('/api/v1/members', memberRouter);

// ===== 错误处理 =====
app.use((err, req, res, _next) => {
  const log = {
    timestamp: new Date().toISOString(),
    level: 'ERROR',
    service: 'member-svc',
    message: err.message,
    stack: err.stack,
  };
  process.stderr.write(JSON.stringify(log) + '\n');
  res.status(500).json({ error: 'Internal Server Error' });
});

// ===== 启动 =====
const server = app.listen(PORT, () => {
  process.stdout.write(JSON.stringify({
    timestamp: new Date().toISOString(),
    level: 'INFO',
    service: 'member-svc',
    message: `member-svc started on port ${PORT}`,
  }) + '\n');
});

// 优雅停机
process.on('SIGTERM', () => {
  server.close(() => {
    process.stdout.write(JSON.stringify({
      timestamp: new Date().toISOString(),
      level: 'INFO',
      service: 'member-svc',
      message: 'member-svc gracefully stopped',
    }) + '\n');
    process.exit(0);
  });
});

module.exports = { app };
