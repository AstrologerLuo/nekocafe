/**
 * 健康检查路由
 */
'use strict';

const express = require('express');
const healthRouter = express.Router();

healthRouter.get('/healthz', (req, res) => {
  res.status(200).json({ status: 'ok', service: 'member-svc' });
});

healthRouter.get('/readyz', (req, res) => {
  // TODO: 生产环境检查 DB 连接状态
  res.status(200).json({ status: 'ready' });
});

module.exports = { healthRouter };
