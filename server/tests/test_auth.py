"""认证接口测试"""

from app.middleware.auth import create_token


class TestAuthLogin:
    async def test_login_with_dev_code(self, client):
        """开发模式：使用 code 作为 openid"""
        resp = await client.post("/api/auth/login", json={"code": "test_code_123"})
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert data["role"] == "owner"
        assert data["is_new"] is True

    async def test_login_existing_user(self, client, owner_user):
        """已注册用户再次登录"""
        resp = await client.post(
            "/api/auth/login", json={"code": owner_user.openid.replace("dev_", "")}
        )
        # 开发模式用 code 作为 openid 前缀加了 dev_
        # 这里直接用 openid 对应的 code 来测试
        assert resp.status_code == 200

    async def test_login_missing_code(self, client):
        """缺少 code 字段"""
        resp = await client.post("/api/auth/login", json={})
        assert resp.status_code == 422


class TestAuthProfile:
    async def test_get_profile_authenticated(self, client, owner_token):
        """认证用户获取个人信息"""
        resp = await client.get(
            "/api/auth/profile",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["role"] == "owner"
        assert data["nickname"] == "业主A"

    async def test_get_profile_unauthenticated(self, client):
        """未认证访问"""
        resp = await client.get("/api/auth/profile")
        assert resp.status_code == 403  # HTTPBearer 要求


class TestJWT:
    async def test_create_and_decode_token(self, db_session):
        """token 生成和解码"""
        from app.middleware.auth import decode_token

        token = create_token("U12345678", "owner")
        payload = decode_token(token)
        assert payload["sub"] == "U12345678"
        assert payload["role"] == "owner"
        assert "exp" in payload

    async def test_invalid_token(self, client):
        """无效 token 访问受保护接口"""
        resp = await client.get(
            "/api/auth/profile",
            headers={"Authorization": "Bearer invalid.jwt.token"},
        )
        assert resp.status_code == 401
