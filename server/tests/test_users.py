"""用户管理接口测试"""

from app.middleware.auth import create_token


class TestUserProfile:
    async def test_update_profile(self, client, owner_token):
        """更新用户信息"""
        resp = await client.put(
            "/api/users/profile",
            json={"nickname": "新昵称", "phone": "13800138000"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_get_properties(self, client, owner_token):
        """获取房产列表"""
        resp = await client.get(
            "/api/users/properties",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    async def test_verify_identity(self, client, owner_token):
        """身份核验"""
        resp = await client.post(
            "/api/users/verify",
            json={"level": 1, "data": {}},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["verifiedLevel"] >= 1


class TestUserAdmin:
    async def test_get_user_list_requires_property_or_committee(self, client, owner_token):
        """业主不能访问用户列表"""
        resp = await client.get(
            "/api/users/list",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 403

    async def test_get_user_list_as_property(self, client, property_token):
        """物业可以访问用户列表"""
        resp = await client.get(
            "/api/users/list",
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data

    async def test_get_user_list_with_filter(self, client, committee_token):
        """按角色过滤用户列表"""
        resp = await client.get(
            "/api/users/list?role=owner",
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        for u in data["data"]:
            assert u["role"] == "owner"

    async def test_update_user_role(self, client, committee_token, owner_user):
        """业委会修改用户角色"""
        resp = await client.put(
            f"/api/users/{owner_user.id}/role",
            json={"role": "property"},
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_update_user_role_requires_committee(self, client, property_token, owner_user):
        """物业不能修改用户角色"""
        resp = await client.put(
            f"/api/users/{owner_user.id}/role",
            json={"role": "property"},
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert resp.status_code == 403

    async def test_toggle_user_active(self, client, committee_token, owner_user):
        """业委会启用/禁用用户"""
        resp = await client.put(
            f"/api/users/{owner_user.id}/active",
            json={"isActive": False},
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    async def test_update_role_invalid_role(self, client, committee_token, owner_user):
        """无效角色"""
        resp = await client.put(
            f"/api/users/{owner_user.id}/role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 422  # Pydantic 验证失败
