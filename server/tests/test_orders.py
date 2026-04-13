"""工单接口测试"""


class TestOrderList:
    async def test_get_order_list(self, client, owner_token):
        """获取工单列表"""
        resp = await client.get(
            "/api/orders",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert "total" in data


class TestOrderCreate:
    async def test_create_order(self, client, owner_token):
        """业主提交报修"""
        resp = await client.post(
            "/api/orders",
            json={
                "category": "水电",
                "subCategory": "漏水",
                "description": "厨房水龙头漏水",
                "contactPhone": "13800138000",
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "orderId" in data

    async def test_create_order_missing_fields(self, client, owner_token):
        """缺少必填字段"""
        resp = await client.post(
            "/api/orders",
            json={"category": "水电"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 422


class TestOrderWorkflow:
    async def test_full_order_lifecycle(self, client, owner_token, property_token):
        """完整工单生命周期：创建→接单→处理→完成→评价"""
        # 1. 创建
        create_resp = await client.post(
            "/api/orders",
            json={
                "category": "水电",
                "subCategory": "漏水",
                "description": "厨房水龙头漏水",
                "contactPhone": "13800138000",
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert create_resp.status_code == 200
        order_id = create_resp.json()["orderId"]

        # 2. 获取详情
        detail_resp = await client.get(
            f"/api/orders/{order_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert detail_resp.status_code == 200
        assert detail_resp.json()["status"] == "submitted"

        # 3. 接单
        accept_resp = await client.post(
            f"/api/orders/{order_id}/accept",
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert accept_resp.status_code == 200

        # 4. 处理
        process_resp = await client.post(
            f"/api/orders/{order_id}/process",
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert process_resp.status_code == 200

        # 5. 完成
        complete_resp = await client.post(
            f"/api/orders/{order_id}/complete",
            json={"note": "已修好", "completionPhotos": []},
            headers={"Authorization": f"Bearer {property_token}"},
        )
        assert complete_resp.status_code == 200

        # 6. 评价
        rate_resp = await client.post(
            f"/api/orders/{order_id}/rate",
            json={"rating": 5, "comment": "非常满意"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert rate_resp.status_code == 200

    async def test_accept_requires_property(self, client, owner_token):
        """业主不能接单"""
        resp = await client.post(
            "/api/orders/nonexistent/accept",
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert resp.status_code == 403

    async def test_rework_order(self, client, owner_token, property_token):
        """复修流程"""
        # 创建
        create_resp = await client.post(
            "/api/orders",
            json={
                "category": "水电",
                "description": "水龙头又漏了",
                "contactPhone": "13800138000",
            },
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        order_id = create_resp.json()["orderId"]

        # 接单→处理→完成
        await client.post(f"/api/orders/{order_id}/accept", headers={"Authorization": f"Bearer {property_token}"})
        await client.post(f"/api/orders/{order_id}/process", headers={"Authorization": f"Bearer {property_token}"})
        await client.post(f"/api/orders/{order_id}/complete", json={"note": "已修"}, headers={"Authorization": f"Bearer {property_token}"})

        # 复修
        rework_resp = await client.post(
            f"/api/orders/{order_id}/rework",
            json={"reason": "还是漏"},
            headers={"Authorization": f"Bearer {owner_token}"},
        )
        assert rework_resp.status_code == 200
