"""公告接口测试"""


class TestAnnouncementList:
    async def test_get_announcement_list(self, client, owner_token):
        """获取公告列表"""
        resp = await client.get(
            "/api/announcements",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data


class TestAnnouncementCRUD:
    async def test_create_announcement(self, client, property_token):
        """物业发布公告"""
        resp = await client.post(
            "/api/announcements",
            json={
                "title": "停水通知",
                "content": "明天上午8-12点停水维修",
                "type": "notice",
                "publisher": "物业",
                "publisherName": "物业A",
            },
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "id" in data

    async def test_create_announcement_by_committee(self, client, committee_token):
        """业委会也可以发布公告"""
        resp = await client.post(
            "/api/announcements",
            json={
                "title": "投票结果公告",
                "content": "关于XX的投票结果",
                "type": "vote",
            },
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 200

    async def test_create_announcement_requires_role(self, client, owner_token):
        """业主不能发布公告"""
        resp = await client.post(
            "/api/announcements",
            json={"title": "测试", "content": "内容"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 403

    async def test_update_announcement(self, client, property_token):
        """编辑公告"""
        # 创建
        create_resp = await client.post(
            "/api/announcements",
            json={"title": "原始标题", "content": "原始内容"},
            headers={"Authorization": f"Bearer {property_token}"},
        )
        ann_id = create_resp.json()["id"]

        # 编辑
        update_resp = await client.put(
            f"/api/announcements/{ann_id}",
            json={"title": "修改标题", "content": "修改内容"},
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert update_resp.status_code == 200

    async def test_delete_announcement(self, client, property_token):
        """删除公告"""
        create_resp = await client.post(
            "/api/announcements",
            json={"title": "待删除", "content": "内容"},
            headers={"Authorization": f"Bearer {property_token}"},
        )
        ann_id = create_resp.json()["id"]

        delete_resp = await client.delete(
            f"/api/announcements/{ann_id}",
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert delete_resp.status_code == 200

    async def test_delete_nonexistent(self, client, property_token):
        """删除不存在的公告"""
        resp = await client.delete(
            "/api/announcements/nonexistent",
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert resp.status_code == 404


class TestAnnouncementDetail:
    async def test_get_detail_auto_reads(self, client, property_token, owner_token):
        """获取详情自动记录阅读"""
        # 创建
        create_resp = await client.post(
            "/api/announcements",
            json={"title": "阅读测试", "content": "内容"},
            headers={"Authorization": f"Bearer {property_token}"},
        )
        ann_id = create_resp.json()["id"]

        # 读取详情
        detail_resp = await client.get(
            f"/api/announcements/{ann_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert detail_resp.status_code == 200
        data = detail_resp.json()
        assert data["readCount"] >= 1
