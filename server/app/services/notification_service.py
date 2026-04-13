"""通知服务 — 5级推送策略 + 微信订阅消息封装"""

import json
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, NotificationSubscription, User
from app.utils.logger import get_logger

logger = get_logger("notification_service")

# 5级推送策略
# 1. urgent (紧急): 如燃气停供、电梯故障 → 微信服务消息+订阅消息双推
# 2. important (重要): 如投票发起、重大决策 → 订阅消息推送
# 3. info (普通): 如工单状态更新 → 小程序内消息中心
# 4. activity (活动): 如社区活动 → 首页信息流推荐
# 5. ad (广告): → 仅活动板块

# 消息类型映射
MSG_TYPES = {
    "vote_remind": "投票提醒",
    "order_update": "工单更新",
    "finance_publish": "财务公示",
    "announcement": "公告通知",
    "complaint_reply": "投诉回复",
}

# 微信订阅消息模板ID映射（需在小程序后台配置）
WECHAT_TEMPLATES = {
    "vote_remind": "",       # 投票提醒模板ID
    "order_update": "",      # 工单更新模板ID
    "finance_publish": "",   # 财务公示模板ID
    "announcement": "",      # 公告通知模板ID
    "complaint_reply": "",   # 投诉回复模板ID
}


class NotificationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        user_id: str,
        community_id: str,
        title: str,
        content: str,
        notification_type: str = "info",
        biz_type: str = "",
        biz_id: str = "",
    ) -> Notification:
        """创建站内通知"""
        notification = Notification(
            community_id=community_id,
            user_id=user_id,
            title=title,
            content=content,
            type=notification_type,
            biz_type=biz_type,
            biz_id=biz_id,
        )
        self.db.add(notification)
        await self.db.flush()

        # 根据推送策略决定是否发微信订阅消息
        if notification_type in ("urgent", "important"):
            await self._send_wechat_subscribe(user_id, title, content, biz_type)

        logger.info(f"通知创建: user={user_id}, type={notification_type}, title={title}")
        return notification

    async def create_bulk(
        self,
        user_ids: list[str],
        community_id: str,
        title: str,
        content: str,
        notification_type: str = "info",
        biz_type: str = "",
        biz_id: str = "",
    ) -> int:
        """批量创建通知（如投票发起时通知全体业主）"""
        count = 0
        for uid in user_ids:
            await self.create_notification(
                user_id=uid,
                community_id=community_id,
                title=title,
                content=content,
                notification_type=notification_type,
                biz_type=biz_type,
                biz_id=biz_id,
            )
            count += 1
        return count

    async def get_list(
        self,
        user_id: str,
        *,
        is_read: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Notification], int, int]:
        """获取通知列表，返回 (items, total, unread_count)"""
        query = select(Notification).where(Notification.user_id == user_id)
        count_query = select(func.count(Notification.id)).where(Notification.user_id == user_id)

        if is_read is not None:
            query = query.where(Notification.is_read == is_read)
            count_query = count_query.where(Notification.is_read == is_read)

        # 未读数
        unread_result = await self.db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id, Notification.is_read == False
            )
        )
        unread_count = unread_result.scalar() or 0

        # 总数
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Notification.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total, unread_count

    async def mark_read(self, notification_id: str, user_id: str) -> None:
        """标记已读"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
            )
        )
        notification = result.scalar_one_or_none()
        if notification and not notification.is_read:
            notification.is_read = True
            self.db.add(notification)
            await self.db.flush()

    async def mark_all_read(self, user_id: str) -> None:
        """全部标记已读"""
        result = await self.db.execute(
            select(Notification).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        )
        for n in result.scalars().all():
            n.is_read = True
            self.db.add(n)
        await self.db.flush()

    async def get_subscriptions(self, user_id: str) -> list[NotificationSubscription]:
        """获取用户订阅设置"""
        result = await self.db.execute(
            select(NotificationSubscription).where(NotificationSubscription.user_id == user_id)
        )
        subs = result.scalars().all()
        # 确保所有类型都有记录
        existing_types = {s.msg_type for s in subs}
        for msg_type in MSG_TYPES:
            if msg_type not in existing_types:
                sub = NotificationSubscription(
                    user_id=user_id, msg_type=msg_type, is_subscribed=True
                )
                self.db.add(sub)
                subs.append(sub)
        await self.db.flush()
        return subs

    async def update_subscription(self, user_id: str, msg_type: str, is_subscribed: bool) -> None:
        """更新订阅设置"""
        result = await self.db.execute(
            select(NotificationSubscription).where(
                NotificationSubscription.user_id == user_id,
                NotificationSubscription.msg_type == msg_type,
            )
        )
        sub = result.scalar_one_or_none()
        if sub:
            sub.is_subscribed = is_subscribed
        else:
            sub = NotificationSubscription(
                user_id=user_id, msg_type=msg_type, is_subscribed=is_subscribed
            )
        self.db.add(sub)
        await self.db.flush()

    async def _send_wechat_subscribe(self, user_id: str, title: str, content: str, biz_type: str) -> None:
        """发送微信订阅消息（需要用户订阅且配置模板ID）"""
        # 检查用户是否订阅了该类型
        msg_type = self._biz_type_to_msg_type(biz_type)
        if not msg_type:
            return

        result = await self.db.execute(
            select(NotificationSubscription).where(
                NotificationSubscription.user_id == user_id,
                NotificationSubscription.msg_type == msg_type,
                NotificationSubscription.is_subscribed == True,
            )
        )
        if not result.scalar_one_or_none():
            return

        template_id = WECHAT_TEMPLATES.get(msg_type, "")
        if not template_id:
            logger.debug(f"微信订阅消息模板未配置: {msg_type}，跳过推送")
            return

        # 实际调用微信 subscribeMessage API
        # 需要 access_token + 用户 openid
        # 此处预留接口，待配置微信小程序后启用
        logger.info(f"微信订阅消息待发送: user={user_id}, template={template_id}, title={title}")

    def _biz_type_to_msg_type(self, biz_type: str) -> str:
        """业务类型转消息类型"""
        mapping = {
            "vote": "vote_remind",
            "order": "order_update",
            "finance": "finance_publish",
            "announcement": "announcement",
            "complaint": "complaint_reply",
        }
        return mapping.get(biz_type, "")
