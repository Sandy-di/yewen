"""健康检查接口测试"""


class TestHealthCheck:
    async def test_health_returns_ok(self, client):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["app"] == "业问"
        assert data["version"] == "1.0.0"
        assert data["database"] == "ok"
