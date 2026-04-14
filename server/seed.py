"""
种子数据脚本 — 创建社区、3个角色用户、示例投票/工单/财务/公告数据

用法: python seed.py
"""

import asyncio
import sys
import os

# 确保可以导入 app 模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app.database import engine, async_session, Base, init_db
from app.models import (
    Community, User, UserProperty,
    Vote, VoteOption, VoteRecord,
    RepairOrder, OrderTimeline,
    FinanceReport, FinanceItem,
    Announcement, AnnouncementRead,
    Complaint, ComplaintReply,
    gen_id,
)


async def seed():
    """执行种子数据填充"""
    # 先初始化数据库（建表）
    await init_db()

    async with async_session() as session:
        # 检查是否已有数据
        from sqlalchemy import select, func
        result = await session.execute(select(func.count(Community.id)))
        if result.scalar() > 0:
            print("⚠️  数据库已有数据，跳过种子数据填充")
            return

        print("🌱 开始填充种子数据...")

        # ===== 1. 社区 =====
        community = Community(
            id=gen_id("C"),
            name="黑金时代广场",
            total_units=512,
            total_area=45600.0,
            address="杭州市西湖区黑金路88号",
        )
        session.add(community)
        await session.flush()
        print(f"  ✅ 社区: {community.name} ({community.id})")

        # ===== 2. 用户（3个角色） =====
        owner = User(
            openid="oDev_Owner_001",
            nickname="张先生",
            phone="138****5678",
            role="owner",
            verified_level=2,
            community_id=community.id,
        )
        property_staff = User(
            openid="oDev_Property_001",
            nickname="物业服务中心",
            phone="139****1234",
            role="property",
            verified_level=3,
            community_id=community.id,
        )
        committee = User(
            openid="oDev_Committee_001",
            nickname="张主任",
            phone="137****5678",
            role="committee",
            verified_level=4,
            community_id=community.id,
        )
        session.add_all([owner, property_staff, committee])
        await session.flush()
        print(f"  ✅ 用户: {owner.nickname}({owner.id}), {property_staff.nickname}({property_staff.id}), {committee.nickname}({committee.id})")

        # ===== 3. 房产 =====
        prop1 = UserProperty(
            user_id=owner.id,
            community_id=community.id,
            building="3栋",
            unit="1单元",
            room_no="502",
            usable_area=89.5,
            is_default=True,
        )
        session.add(prop1)
        await session.flush()
        print(f"  ✅ 房产: {prop1.building}{prop1.unit}{prop1.room_no} ({prop1.id})")

        # ===== 4. 投票 =====
        vote1 = Vote(
            community_id=community.id,
            title="关于小区大门更换的投票",
            description="现有小区东门及南门大门使用已超过10年，锈蚀严重且存在安全隐患。业委会提议使用公共维修基金更换为智能门禁系统，预算约28万元。请各位业主投票表决。",
            verification_level=3,
            vote_type="double_majority",
            status="active",
            start_time=datetime(2026, 4, 5, 8, 0),
            end_time=datetime(2026, 4, 15, 18, 0),
            total_properties=512,
            participated_count=234,
            participated_area=18920,
            total_area=45600,
            created_by=committee.id,
        )
        vote2 = Vote(
            community_id=community.id,
            title="关于绿化改造方案的投票",
            description="为提升小区环境品质，拟对中心花园区域进行绿化升级改造，增加休闲座椅和儿童游乐设施。预算15万元。",
            verification_level=2,
            vote_type="double_majority",
            status="ended",
            start_time=datetime(2026, 3, 20, 8, 0),
            end_time=datetime(2026, 3, 30, 18, 0),
            total_properties=512,
            participated_count=389,
            participated_area=34200,
            total_area=45600,
            created_by=committee.id,
            result_hash="0xabc123def456",
            result="passed",
            result_summary="参与户数76%（389/512），参与面积75%（34,200/45,600㎡）。同意户数92%（356/389），同意面积91%（31,200/34,200㎡）。达到双过半标准，投票通过。",
        )
        vote3 = Vote(
            community_id=community.id,
            title="关于物业费调整的投票",
            description="鉴于人力成本上涨及服务升级需求，拟将物业费从2.5元/㎡调整为3.0元/㎡，同时增加以下服务：24小时安保巡逻、公共区域WiFi覆盖、垃圾分类指导。",
            verification_level=4,
            vote_type="double_three_quarters",
            status="active",
            start_time=datetime(2026, 4, 8, 8, 0),
            end_time=datetime(2026, 4, 22, 18, 0),
            total_properties=512,
            participated_count=156,
            participated_area=12800,
            total_area=45600,
            created_by=committee.id,
        )
        session.add_all([vote1, vote2, vote3])
        await session.flush()

        # 投票选项
        opts_data = [
            (vote1.id, [("同意更换", 189, 15230), ("不同意", 35, 2890), ("弃权", 10, 800)]),
            (vote2.id, [("同意改造", 356, 31200), ("不同意", 25, 2200), ("弃权", 8, 800)]),
            (vote3.id, [("同意调整", 98, 8100), ("不同意", 48, 3900), ("弃权", 10, 800)]),
        ]
        for vote_id, options in opts_data:
            for label, count, area in options:
                session.add(VoteOption(vote_id=vote_id, label=label, count=count, area=area))
        await session.flush()
        print(f"  ✅ 投票: 3个投票 + 9个选项")

        # ===== 5. 报修工单 =====
        order1 = RepairOrder(
            community_id=community.id,
            user_id=owner.id,
            category="access",
            sub_category="门禁故障",
            description="小区东门门禁系统故障，业主无法刷卡进出，已持续2天。",
            status="processing",
            property_id=prop1.id,
            contact_phone=owner.phone,
            accepted_at=datetime(2026, 4, 10, 14, 30),
            accepted_by=property_staff.id,
            acceptor_phone=property_staff.phone,
            estimated_time="15:00",
            sla_level=24,
            sla_deadline=datetime(2026, 4, 11, 14, 23),
        )
        order2 = RepairOrder(
            community_id=community.id,
            user_id=owner.id,
            category="water_elec",
            sub_category="漏水",
            description="5栋地下车库入口处天花板漏水，雨水天气尤为严重。",
            status="completed",
            property_id=prop1.id,
            contact_phone=owner.phone,
            accepted_at=datetime(2026, 4, 8, 9, 45),
            accepted_by=property_staff.id,
            completed_at=datetime(2026, 4, 8, 16, 30),
            completion_note="已重新做防水处理并修补裂缝",
            rating=5,
            rating_comment="处理及时，效果不错",
            sla_level=24,
            sla_deadline=datetime(2026, 4, 9, 9, 15),
        )
        order3 = RepairOrder(
            community_id=community.id,
            user_id=owner.id,
            category="facility",
            sub_category="电梯",
            description="7栋2单元电梯运行时有异响，且偶尔出现停顿。",
            status="pending_check",
            property_id=prop1.id,
            contact_phone=owner.phone,
            accepted_at=datetime(2026, 4, 7, 20, 30),
            accepted_by=property_staff.id,
            completed_at=datetime(2026, 4, 8, 11, 0),
            completion_note="更换电梯钢丝绳和导轨滑块，已通过安全检测",
            sla_level=24,
            sla_deadline=datetime(2026, 4, 8, 20, 10),
        )
        session.add_all([order1, order2, order3])
        await session.flush()

        # 时间线
        timelines_data = [
            (order1.id, [
                ("业主提交报修", "submitted"),
                ("物业已接单，张师傅预计15:00上门", "accepted"),
                ("开始维修，正在更换门禁控制模块", "processing"),
            ]),
            (order2.id, [
                ("业主提交报修", "submitted"),
                ("李师傅已接单", "accepted"),
                ("开始维修", "processing"),
                ("维修完成，已重新做防水处理", "completed"),
                ("业主验收通过，评价5星", "verified"),
            ]),
            (order3.id, [
                ("业主提交报修", "submitted"),
                ("王师傅已接单，明早处理", "accepted"),
                ("开始维修，联系电梯维保公司", "processing"),
                ("维修完成，更换钢丝绳和导轨", "completed"),
            ]),
        ]
        for order_id, timelines in timelines_data:
            for content, type_str in timelines:
                session.add(OrderTimeline(order_id=order_id, content=content, type=type_str))
        await session.flush()
        print(f"  ✅ 工单: 3个工单 + 时间线")

        # ===== 6. 财务报表 =====
        report1 = FinanceReport(
            community_id=community.id,
            month="2026-03",
            title="2026年3月物业收支报表",
            status="published",
            submitted_by=property_staff.id,
            submitted_at=datetime(2026, 4, 5, 10, 0),
            approved_by=committee.id,
            approved_at=datetime(2026, 4, 6, 9, 0),
            total_income=128560.00,
            total_expense=95230.50,
            balance=33329.50,
        )
        report2 = FinanceReport(
            community_id=community.id,
            month="2026-02",
            title="2026年2月物业收支报表",
            status="published",
            submitted_by=property_staff.id,
            submitted_at=datetime(2026, 3, 5, 10, 0),
            approved_by=committee.id,
            approved_at=datetime(2026, 3, 6, 14, 0),
            total_income=115200.00,
            total_expense=88650.00,
            balance=26550.00,
        )
        report3 = FinanceReport(
            community_id=community.id,
            month="2026-04",
            title="2026年4月物业收支报表",
            status="pending",
            submitted_by=property_staff.id,
            submitted_at=datetime(2026, 4, 10, 16, 0),
            total_income=0,
            total_expense=0,
            balance=0,
        )
        session.add_all([report1, report2, report3])
        await session.flush()

        # 财务明细
        finance_items = [
            (report1.id, "income", "物业费", 102400.00, "3月物业费收缴"),
            (report1.id, "income", "停车费", 18600.00, "地下车库停车费"),
            (report1.id, "income", "广告位收入", 5600.00, "电梯广告位出租"),
            (report1.id, "income", "公共收益", 1960.00, "快递柜场地费"),
            (report1.id, "expense", "人员工资", 52000.00, "物业人员3月工资"),
            (report1.id, "expense", "维修费", 12800.00, "电梯维保+门禁维修"),
            (report1.id, "expense", "绿化费", 8600.50, "绿化养护+春季补种"),
            (report1.id, "expense", "水电费", 12600.00, "公共区域水电费"),
            (report1.id, "expense", "保洁费", 5230.00, "保洁服务费"),
            (report1.id, "expense", "办公费", 4000.00, "办公用品+打印"),
            (report2.id, "income", "物业费", 96000.00, "2月物业费收缴"),
            (report2.id, "income", "停车费", 15200.00, "地下车库停车费"),
            (report2.id, "income", "广告位收入", 4000.00, "电梯广告位出租"),
            (report2.id, "expense", "人员工资", 52000.00, "物业人员2月工资"),
            (report2.id, "expense", "维修费", 8500.00, "路灯维修+管道疏通"),
            (report2.id, "expense", "绿化费", 3200.00, "冬季绿化维护"),
            (report2.id, "expense", "水电费", 18500.00, "公共区域水电费(含春节照明)"),
            (report2.id, "expense", "保洁费", 5450.00, "保洁服务费"),
            (report2.id, "expense", "办公费", 1000.00, "办公用品"),
        ]
        for report_id, item_type, category, amount, desc in finance_items:
            session.add(FinanceItem(
                report_id=report_id,
                item_type=item_type,
                category=category,
                amount=amount,
                description=desc,
            ))
        await session.flush()
        print(f"  ✅ 财务: 3个报表 + {len(finance_items)}条明细")

        # ===== 7. 公告 =====
        announcements = [
            Announcement(
                community_id=community.id,
                title="关于小区大门更换投票的通知",
                content="各位业主：\n\n根据《民法典》相关规定，现就小区大门更换事宜发起业主投票。投票时间为4月5日至4月15日，请各位业主积极参与。\n\n本次投票需完成L3身份核验后方可参与，请提前完成核验。",
                type="vote",
                publisher="业委会",
                publisher_name="张主任",
                is_top=True,
                created_by=committee.id,
                created_at=datetime(2026, 4, 4, 9, 0),
            ),
            Announcement(
                community_id=community.id,
                title="4月小区绿化养护安排通知",
                content="各位业主：\n\n4月绿化养护工作安排如下：\n1. 4月12日-13日：中心花园春季补种\n2. 4月15日-16日：行道树修剪\n3. 4月20日：病虫害防治喷药\n\n喷药期间请注意关窗，照看好宠物和儿童。",
                type="notice",
                publisher="物业",
                publisher_name="物业服务中心",
                is_top=False,
                created_by=property_staff.id,
                created_at=datetime(2026, 4, 8, 10, 0),
            ),
            Announcement(
                community_id=community.id,
                title="清明假期物业服务时间调整",
                content="各位业主：\n\n清明假期（4月4日-6日）期间，物业服务中心营业时间调整为：9:00-17:00。\n\n24小时报修热线正常服务。",
                type="notice",
                publisher="物业",
                publisher_name="物业服务中心",
                is_top=False,
                created_by=property_staff.id,
                created_at=datetime(2026, 4, 3, 15, 0),
            ),
            Announcement(
                community_id=community.id,
                title="2026年第一季度财务公示",
                content='各位业主：\n\n2026年第一季度（1-3月）物业财务报表已完成审批并公示。详细收支明细请查看"公示"页面。\n\n如有疑问，可联系业委会或物业前台。',
                type="finance",
                publisher="业委会",
                publisher_name="李副主任",
                is_top=False,
                created_by=committee.id,
                created_at=datetime(2026, 4, 1, 10, 0),
            ),
        ]
        session.add_all(announcements)
        await session.flush()
        print(f"  ✅ 公告: {len(announcements)}条")

        # ===== 8. 投诉建议 =====
        complaint1 = Complaint(
            community_id=community.id,
            user_id=owner.id,
            title="地下车库照明不足",
            content="B区地下车库多盏灯已损坏超过两周，光线昏暗存在安全隐患，尤其夜间通行不便。请尽快安排维修。",
            category="service",
            status="replied",
            is_important=False,
            sla_hours=48,
            sla_deadline=datetime(2026, 4, 13, 10, 0),
        )
        complaint2 = Complaint(
            community_id=community.id,
            user_id=owner.id,
            title="公共区域噪音扰民",
            content="近期夜间（22:00后）有业主在小区花园区域大声喧哗、播放音乐，严重影响周边住户休息。希望物业加强巡逻管理。",
            category="environment",
            status="submitted",
            is_important=True,
            sla_hours=48,
            sla_deadline=datetime(2026, 4, 16, 9, 0),
        )
        complaint3 = Complaint(
            community_id=community.id,
            user_id=owner.id,
            title="物业费收支不透明",
            content="2025年第四季度的财务公示迟迟未发布，业主无法了解公共收益使用情况。要求业委会督促物业尽快公示。",
            category="fee",
            status="resolved",
            is_important=True,
            resolved_at=datetime(2026, 4, 10, 16, 0),
        )
        session.add_all([complaint1, complaint2, complaint3])
        await session.flush()

        # 投诉回复
        replies = [
            ComplaintReply(
                complaint_id=complaint1.id,
                user_id=property_staff.id,
                content="已安排电工师傅明天上午检修B区车库照明，预计明晚恢复正常。给您带来不便敬请谅解。",
                reply_type="reply",
            ),
            ComplaintReply(
                complaint_id=complaint3.id,
                user_id=committee.id,
                content="已督促物业提交Q4财务报表，预计本周内完成审批并公示。",
                reply_type="supervise",
            ),
            ComplaintReply(
                complaint_id=complaint3.id,
                user_id=property_staff.id,
                content="Q4财务报表已完成提交，正在等待业委会审批，审批通过后将第一时间公示。",
                reply_type="reply",
            ),
        ]
        session.add_all(replies)
        await session.flush()
        print(f"  ✅ 投诉: 3条 + 回复")

        await session.commit()
        print("\n🎉 种子数据填充完成！")
        print("\n📋 测试账号:")
        print(f"  业主: openid=oDev_Owner_001 → {owner.nickname} (id={owner.id})")
        print(f"  物业: openid=oDev_Property_001 → {property_staff.nickname} (id={property_staff.id})")
        print(f"  业委会: openid=oDev_Committee_001 → {committee.nickname} (id={committee.id})")


if __name__ == "__main__":
    asyncio.run(seed())
