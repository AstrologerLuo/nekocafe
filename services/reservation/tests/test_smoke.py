"""冒烟测试 - 验证服务基本启动与健康检查"""
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_healthz():
    """健康检查端点应返回 200"""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readyz():
    """就绪检查端点应返回 200"""
    response = client.get("/readyz")
    assert response.status_code == 200


def test_openapi_docs():
    """OpenAPI 文档端点应可访问"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_smoke():
    """基础断言：1+1=2"""
    assert 1 + 1 == 2
