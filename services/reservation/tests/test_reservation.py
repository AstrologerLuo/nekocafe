"""预约业务单元测试"""
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def _reservation_payload(**kwargs):
    """构造合法的预约请求体"""
    base = {
        "store_id": 1,
        "table_id": 10,
        "member_id": 100,
        "party_size": 2,
        "reserved_at": datetime(2026, 6, 1, 12, 0, tzinfo=timezone.utc).isoformat(),
        "note": "靠窗",
    }
    base.update(kwargs)
    return base


class TestCreateReservation:
    def test_create_success(self):
        """成功创建预约"""
        resp = client.post("/api/v1/reservations/", json=_reservation_payload())
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "confirmed"
        assert data["store_id"] == 1
        assert data["party_size"] == 2

    def test_create_invalid_party_size(self):
        """超出人数上限应返回 422"""
        resp = client.post("/api/v1/reservations/", json=_reservation_payload(party_size=25))
        assert resp.status_code == 422

    def test_create_missing_store_id(self):
        """缺少必填字段应返回 422"""
        payload = _reservation_payload()
        del payload["store_id"]
        resp = client.post("/api/v1/reservations/", json=payload)
        assert resp.status_code == 422


class TestGetReservation:
    def test_get_existing(self):
        """查询已存在的预约"""
        create_resp = client.post("/api/v1/reservations/", json=_reservation_payload())
        rid = create_resp.json()["id"]

        get_resp = client.get(f"/api/v1/reservations/{rid}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == rid

    def test_get_not_found(self):
        """查询不存在的预约应返回 404"""
        resp = client.get("/api/v1/reservations/nonexistent-id")
        assert resp.status_code == 404


class TestCancelReservation:
    def test_cancel_existing(self):
        """取消已有预约"""
        create_resp = client.post("/api/v1/reservations/", json=_reservation_payload())
        rid = create_resp.json()["id"]

        cancel_resp = client.delete(f"/api/v1/reservations/{rid}")
        assert cancel_resp.status_code == 204

    def test_cancel_not_found(self):
        """取消不存在的预约应返回 404"""
        resp = client.delete("/api/v1/reservations/nonexistent-id")
        assert resp.status_code == 404
