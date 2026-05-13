#!/usr/bin/env python3
"""
seed.py - 测试数据种子脚本
为 dev/staging 环境生成匿名化测试数据
"""
import os
import random
from datetime import datetime, timedelta, timezone

API_BASE = os.getenv("API_BASE", "http://localhost")
MEMBER_URL = f"{API_BASE}:8082/api/v1/members"
RESERVATION_URL = f"{API_BASE}:8081/api/v1/reservations"

SAMPLE_USERNAMES = [f"test_user_{i:03d}" for i in range(1, 21)]
SAMPLE_STORES = list(range(1, 6))
SAMPLE_TABLES = list(range(1, 11))

try:
    import httpx

    def seed_members():
        """创建 20 个测试会员"""
        member_ids = []
        with httpx.Client(timeout=10) as client:
            for username in SAMPLE_USERNAMES:
                resp = client.post(MEMBER_URL + "/register", json={
                    "username": username,
                    "email": f"{username}@test.nekocafe.local",
                    "phone": f"1380000{random.randint(1000, 9999)}",
                })
                if resp.status_code == 201:
                    member_ids.append(resp.json()["id"])
                    print(f"  Created member: {username} (id={resp.json()['id']})")
        return member_ids

    def seed_reservations(member_ids):
        """为会员创建预约记录"""
        with httpx.Client(timeout=10) as client:
            for member_id in member_ids[:10]:
                base_time = datetime.now(tz=timezone.utc) + timedelta(days=random.randint(1, 7))
                resp = client.post(RESERVATION_URL + "/", json={
                    "store_id": random.choice(SAMPLE_STORES),
                    "table_id": random.choice(SAMPLE_TABLES),
                    "member_id": member_id,
                    "party_size": random.randint(1, 4),
                    "reserved_at": base_time.isoformat(),
                    "note": "测试预约（seed data）",
                })
                if resp.status_code == 201:
                    print(f"  Created reservation for member {member_id}: {resp.json()['id']}")

    print("=== 开始生成测试数据 ===")
    print("--- 创建会员 ---")
    ids = seed_members()
    print(f"--- 创建预约（共 {len(ids[:10])} 条）---")
    seed_reservations(ids)
    print("=== 种子数据生成完毕 ===")

except ImportError:
    print("httpx not installed. Run: pip install httpx")
    print("Seed data generation skipped.")
