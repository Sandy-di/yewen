"""社区管理接口测试"""


class TestCommunityList:
    async def test_get_communities(self, client, owner_token):
        """获取社区列表"""
        resp = await client.get(
            "/api/communities",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data


class TestCommunityCRUD:
    async def test_create_community(self, client, committee_token):
        """业委会创建社区"""
        resp = await client.post(
            "/api/communities",
            json={
                "name": "测试社区",
                "totalUnits": 500,
                "totalArea": 30000.0,
                "address": "测试地址123号",
            },
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "id" in data

    async def test_create_community_requires_committee(self, client, owner_token):
        """业主不能创建社区"""
        resp = await client.post(
            "/api/communities",
            json={"name": "社区A"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 403

    async def test_get_community_detail(self, client, committee_token, owner_token):
        """获取社区详情"""
        # 创建
        create_resp = await client.post(
            "/api/communities",
            json={"name": "详情社区", "totalUnits": 100},
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        community_id = create_resp.json()["id"]

        # 获取
        detail_resp = await client.get(
            f"/api/communities/{community_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert detail_resp.status_code == 200
        data = detail_resp.json()
        assert data["name"] == "详情社区"

    async def test_update_community(self, client, committee_token):
        """更新社区信息"""
        create_resp = await client.post(
            "/api/communities",
            json={"name": "更新社区"},
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        community_id = create_resp.json()["id"]

        update_resp = await client.put(
            f"/api/communities/{community_id}",
            json={"name": "已更新社区", "totalUnits": 200},
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert update_resp.status_code == 200

    async def test_community_not_found(self, client, owner_token):
        """社区不存在"""
        resp = await client.get(
            "/api/communities/nonexistent",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 404
