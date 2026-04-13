"""财务接口测试"""


class TestFinanceList:
    async def test_get_finance_list(self, client, owner_token):
        """获取财务报表列表"""
        resp = await client.get(
            "/api/finance",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data


class TestFinanceCreate:
    async def test_create_finance_report(self, client, property_token):
        """物业上报财务报表"""
        resp = await client.post(
            "/api/finance",
            json={
                "month": "2026-03",
                "title": "3月财务报表",
                "items": [
                    {"itemType": "income", "category": "物业费", "amount": 50000, "description": "3月物业费收入"},
                    {"itemType": "expense", "category": "维修费", "amount": 5000, "description": "电梯维修"},
                ],
            },
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "reportId" in data

    async def test_create_finance_requires_property(self, client, owner_token):
        """业主不能上报财务"""
        resp = await client.post(
            "/api/finance",
            json={
                "month": "2026-03",
                "title": "3月财务",
                "items": [{"itemType": "income", "category": "物业费", "amount": 1000}],
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 403

    async def test_create_finance_invalid_month(self, client, property_token):
        """月份格式不正确"""
        resp = await client.post(
            "/api/finance",
            json={
                "month": "2026-3",
                "title": "3月财务",
                "items": [{"itemType": "income", "category": "物业费", "amount": 1000}],
            },
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert resp.status_code == 422


class TestFinanceApproveReject:
    async def test_approve_finance(self, client, property_token, committee_token):
        """业委会审批财务"""
        # 创建
        create_resp = await client.post(
            "/api/finance",
            json={
                "month": "2026-04",
                "title": "4月财务",
                "items": [{"itemType": "income", "category": "物业费", "amount": 10000}],
            },
            headers={"Authorization": f"Bearer {property_token}"},
        )
        report_id = create_resp.json()["reportId"]

        # 审批
        approve_resp = await client.post(
            f"/api/finance/{report_id}/approve",
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert approve_resp.status_code == 200

    async def test_reject_finance(self, client, property_token, committee_token):
        """业委会拒绝财务"""
        # 创建
        create_resp = await client.post(
            "/api/finance",
            json={
                "month": "2026-05",
                "title": "5月财务",
                "items": [{"itemType": "income", "category": "物业费", "amount": 10000}],
            },
            headers={"Authorization": f"Bearer {property_token}"},
        )
        report_id = create_resp.json()["reportId"]

        # 拒绝
        reject_resp = await client.post(
            f"/api/finance/{report_id}/reject",
            json={"reason": "数据有误，请核实"},
            headers={"Authorization": f"Bearer {committee_token}"},
        )
        assert reject_resp.status_code == 200

    async def test_approve_requires_committee(self, client, property_token):
        """物业不能审批"""
        create_resp = await client.post(
            "/api/finance",
            json={
                "month": "2026-06",
                "title": "6月财务",
                "items": [{"itemType": "income", "category": "物业费", "amount": 10000}],
            },
            headers={"Authorization": f"Bearer {property_token}"},
        )
        report_id = create_resp.json()["reportId"]

        approve_resp = await client.post(
            f"/api/finance/{report_id}/approve",
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert approve_resp.status_code == 403


class TestFinanceDetail:
    async def test_get_finance_detail(self, client, property_token, owner_token):
        """获取财务报表详情"""
        create_resp = await client.post(
            "/api/finance",
            json={
                "month": "2026-07",
                "title": "7月财务",
                "items": [{"itemType": "income", "category": "物业费", "amount": 8000}],
            },
            headers={"Authorization": f"Bearer {property_token}"},
        )
        report_id = create_resp.json()["reportId"]

        detail_resp = await client.get(
            f"/api/finance/{report_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert detail_resp.status_code == 200
        data = detail_resp.json()
        assert data["title"] == "7月财务"
        assert len(data["items"]) == 1

    async def test_finance_not_found(self, client, owner_token):
        """报表不存在"""
        resp = await client.get(
            "/api/finance/nonexistent",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 404
