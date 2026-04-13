"""投票接口测试"""


class TestVoteList:
    async def test_get_vote_list(self, client, owner_token):
        """获取投票列表"""
        resp = await client.get(
            "/api/votes",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data

    async def test_get_vote_list_unauthenticated(self, client):
        """未认证访问"""
        resp = await client.get("/api/votes")
        assert resp.status_code == 403


class TestVoteCreate:
    async def test_create_vote_as_committee(self, client, committee_token):
        """业委会创建投票"""
        resp = await client.post(
            "/api/votes",
            json={
                "title": "测试投票",
                "description": "这是一个测试投票",
                "verificationLevel": 1,
                "voteType": "simple",
                "options": [{"label": "同意"}, {"label": "反对"}],
            },
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "voteId" in data

    async def test_create_vote_requires_committee(self, client, owner_token):
        """业主不能创建投票"""
        resp = await client.post(
            "/api/votes",
            json={
                "title": "测试投票",
                "options": [{"label": "同意"}, {"label": "反对"}],
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 403

    async def test_create_vote_at_least_two_options(self, client, committee_token):
        """至少需要两个选项"""
        resp = await client.post(
            "/api/votes",
            json={
                "title": "测试投票",
                "options": [{"label": "同意"}],
            },
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert resp.status_code == 422


class TestVoteDetail:
    async def test_get_vote_detail(self, client, committee_token, owner_token):
        """获取投票详情"""
        # 先创建
        create_resp = await client.post(
            "/api/votes",
            json={
                "title": "详情测试",
                "voteType": "simple",
                "options": [{"label": "同意"}, {"label": "反对"}],
            },
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        vote_id = create_resp.json()["voteId"]

        # 再获取
        resp = await client.get(
            f"/api/votes/{vote_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "详情测试"
        assert len(data["options"]) == 2

    async def test_get_vote_detail_not_found(self, client, owner_token):
        """投票不存在"""
        resp = await client.get(
            "/api/votes/nonexistent",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 404


class TestVoteSubmit:
    async def test_submit_vote(self, client, committee_token, owner_token):
        """业主提交投票"""
        # 先提升业主核验等级
        verify_resp = await client.post(
            "/api/users/verify",
            json={"level": 1, "data": {}},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert verify_resp.status_code == 200

        # 创建投票
        create_resp = await client.post(
            "/api/votes",
            json={
                "title": "投票测试",
                "voteType": "simple",
                "verificationLevel": 1,
                "options": [{"label": "同意"}, {"label": "反对"}],
            },
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        vote_id = create_resp.json()["voteId"]

        # 获取选项 ID
        detail_resp = await client.get(
            f"/api/votes/{vote_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        option_id = detail_resp.json()["options"][0]["id"]

        # 提交投票
        resp = await client.post(
            f"/api/votes/{vote_id}/submit",
            json={"optionId": option_id},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
