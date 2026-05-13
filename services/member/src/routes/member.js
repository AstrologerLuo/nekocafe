/**
 * 会员业务路由
 * 提供注册、登录、查询积分等接口
 */
'use strict';

const express = require('express');
const memberRouter = express.Router();

// 内存存储（PoC 演示，生产环境替换为 PostgreSQL）
const members = new Map();
let nextId = 1;

/**
 * POST /api/v1/members/register
 * 会员注册
 */
memberRouter.post('/register', (req, res) => {
  const { username, email, phone } = req.body;
  if (!username || !email) {
    return res.status(400).json({ error: 'username and email are required' });
  }
  const member = {
    id: nextId++,
    username,
    email,
    phone: phone || null,
    points: 0,
    level: 'bronze',
    created_at: new Date().toISOString(),
  };
  members.set(member.id, member);
  return res.status(201).json(member);
});

/**
 * GET /api/v1/members/:id
 * 查询会员信息
 */
memberRouter.get('/:id', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const member = members.get(id);
  if (!member) {
    return res.status(404).json({ error: `Member ${id} not found` });
  }
  return res.status(200).json(member);
});

/**
 * POST /api/v1/members/:id/points
 * 积分变更（消费增加 / 兑换减少）
 */
memberRouter.post('/:id/points', (req, res) => {
  const id = parseInt(req.params.id, 10);
  const member = members.get(id);
  if (!member) {
    return res.status(404).json({ error: `Member ${id} not found` });
  }
  const { delta, reason } = req.body;
  if (typeof delta !== 'number') {
    return res.status(400).json({ error: 'delta must be a number' });
  }
  member.points = Math.max(0, member.points + delta);
  // 更新等级
  if (member.points >= 10000) member.level = 'diamond';
  else if (member.points >= 5000) member.level = 'gold';
  else if (member.points >= 1000) member.level = 'silver';
  else member.level = 'bronze';

  process.stdout.write(JSON.stringify({
    timestamp: new Date().toISOString(),
    level: 'INFO',
    service: 'member-svc',
    event: 'points.changed',
    member_id: id,
    delta,
    reason: reason || '',
    new_points: member.points,
  }) + '\n');

  return res.status(200).json({ id: member.id, points: member.points, level: member.level });
});

module.exports = { memberRouter };
