"""投票服务 — CRUD + 投票提交 + 结果计算"""

import hashlib
import json
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Vote, VoteOption, VoteRecord, User, Community, UserProperty
from app.schemas.vote import VoteCreate
from app.utils.logger import get_logger

logger = get_logger("vote_service")


class VoteService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(
        self,
        community_id: str,
        *,
        status: str | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Vote], int]:
        """获取投票列表，返回 (items, total)"""
        # 自动结束已到期的投票
        now = datetime.now(timezone.utc)
        result = await self.db.execute(
            select(Vote).where(Vote.status == "active", Vote.end_time < now)
        )
        expired_votes = result.scalars().all()
        for v in expired_votes:
            v.status = "ended"
            res, summary, hash_val = self.compute_vote_result(v)
            v.result = res
            v.result_summary = summary
            v.result_hash = hash_val
            self.db.add(v)
        if expired_votes:
            await self.db.flush()

        # 查询
        query = select(Vote).where(Vote.community_id == community_id)
        count_query = select(Vote).where(Vote.community_id == community_id)

        if status and status != "all":
            query = query.where(Vote.status == status)
            count_query = count_query.where(Vote.status == status)
        if keyword:
            query = query.where(Vote.title.contains(keyword))
            count_query = count_query.where(Vote.title.contains(keyword))

        # 总数
        from sqlalchemy import func
        total_result = await self.db.execute(
            select(func.count()).select_from(count_query.subquery())
        )
        total = total_result.scalar() or 0

        # 分页
        query = query.order_by(Vote.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total

    async def get_by_id(self, vote_id: str) -> Vote | None:
        """获取投票详情"""
        result = await self.db.execute(select(Vote).where(Vote.id == vote_id))
        return result.scalar_one_or_none()

    async def create(self, user: User, data: VoteCreate) -> Vote:
        """创建投票"""
        community = None
        if user.community_id:
            result = await self.db.execute(
                select(Community).where(Community.id == user.community_id)
            )
            community = result.scalar_one_or_none()

        vote = Vote(
            community_id=user.community_id,
            title=data.title,
            description=data.description,
            verification_level=data.verificationLevel,
            vote_type=data.voteType,
            status="active",
            start_time=data.startTime or datetime.now(timezone.utc),
            end_time=data.endTime,
            total_properties=community.total_units if community else 0,
            total_area=community.total_area if community else 0,
            created_by=user.id,
        )
        self.db.add(vote)
        await self.db.flush()

        # 创建选项
        for opt in data.options:
            option = VoteOption(vote_id=vote.id, label=opt.label, count=0, area=0)
            self.db.add(option)

        await self.db.flush()
        logger.info(f"投票创建: {vote.id} - {vote.title}")
        return vote

    async def submit_vote(
        self, user: User, vote_id: str, option_id: str
    ) -> str:
        """提交投票，返回交易哈希"""
        # 检查投票
        vote = await self.get_by_id(vote_id)
        if not vote:
            raise ValueError("投票不存在")
        if vote.status != "active":
            raise ValueError("投票未在进行中")

        # 检查核验等级
        if user.verified_level < vote.verification_level:
            raise ValueError(f"需要L{vote.verification_level}核验等级")

        # 检查重复
        exist = await self.db.execute(
            select(VoteRecord).where(
                VoteRecord.vote_id == vote_id,
                VoteRecord.user_id == user.id,
            )
        )
        if exist.scalar_one_or_none():
            raise ValueError("您已投过票")

        # 检查选项
        opt_result = await self.db.execute(
            select(VoteOption).where(VoteOption.id == option_id)
        )
        option = opt_result.scalar_one_or_none()
        if not option or option.vote_id != vote_id:
            raise ValueError("无效的选项")

        # 获取用户房产面积
        user_area = 0
        prop_result = await self.db.execute(
            select(UserProperty).where(UserProperty.user_id == user.id)
        )
        for prop in prop_result.scalars().all():
            user_area += prop.usable_area

        # 事务：插入记录 + 更新计数
        record = VoteRecord(
            vote_id=vote_id, user_id=user.id, option_id=option_id
        )
        self.db.add(record)

        option.count += 1
        option.area += user_area
        self.db.add(option)

        vote.participated_count += 1
        vote.participated_area += user_area
        self.db.add(vote)

        await self.db.flush()

        # 生成哈希
        tx_hash = "0x" + hashlib.sha256(
            f"{vote_id}{user.id}{option_id}".encode()
        ).hexdigest()[:12]

        logger.info(f"投票提交: vote={vote_id}, user={user.id}, option={option_id}")
        return tx_hash

    @staticmethod
    def compute_vote_result(vote: Vote) -> tuple[str, str, str]:
        """计算投票结果（双过半/双四分之三），返回 (result, summary, hash)"""
        total_props = vote.total_properties or 1
        total_area = vote.total_area or 1
        part_count = vote.participated_count
        part_area = vote.participated_area

        agree_option = vote.options[0] if vote.options else None
        agree_count = agree_option.count if agree_option else 0
        agree_area = agree_option.area if agree_option else 0

        if vote.vote_type == "double_majority":
            part_count_ratio = part_count / total_props
            part_area_ratio = part_area / total_area
            agree_count_ratio = agree_count / part_count if part_count > 0 else 0
            agree_area_ratio = agree_area / part_area if part_area > 0 else 0
            threshold = 0.5
            result_str = "passed" if (
                part_count_ratio > threshold and part_area_ratio > threshold
                and agree_count_ratio > threshold and agree_area_ratio > threshold
            ) else "failed"
            summary = (
                f"参与户数{part_count_ratio:.0%}（{part_count}/{total_props}），"
                f"参与面积{part_area_ratio:.0%}（{part_area:.0f}/{total_area:.0f}㎡）。"
                f"同意户数{agree_count_ratio:.0%}（{agree_count}/{part_count}），"
                f"同意面积{agree_area_ratio:.0%}（{agree_area:.0f}/{part_area:.0f}㎡）。"
                f"{'达到双过半标准，投票通过。' if result_str == 'passed' else '未达到双过半标准，投票未通过。'}"
            )
        elif vote.vote_type == "double_three_quarters":
            part_count_ratio = part_count / total_props
            part_area_ratio = part_area / total_area
            agree_count_ratio = agree_count / part_count if part_count > 0 else 0
            agree_area_ratio = agree_area / part_area if part_area > 0 else 0
            threshold = 0.75
            result_str = "passed" if (
                part_count_ratio > threshold and part_area_ratio > threshold
                and agree_count_ratio > threshold and agree_area_ratio > threshold
            ) else "failed"
            summary = (
                f"参与户数{part_count_ratio:.0%}（{part_count}/{total_props}），"
                f"参与面积{part_area_ratio:.0%}（{part_area:.0f}/{total_area:.0f}㎡）。"
                f"同意户数{agree_count_ratio:.0%}（{agree_count}/{part_count}），"
                f"同意面积{agree_area_ratio:.0%}（{agree_area:.0f}/{part_area:.0f}㎡）。"
                f"{'达到双四分之三标准，投票通过。' if result_str == 'passed' else '未达到双四分之三标准，投票未通过。'}"
            )
        else:
            result_str = "passed" if agree_count > (part_count - agree_count) else "failed"
            summary = f"同意{agree_count}票，投票{'通过' if result_str == 'passed' else '未通过'}。"

        # 生成结果哈希
        hash_data = json.dumps({
            "voteId": vote.id,
            "participatedCount": part_count,
            "participatedArea": part_area,
            "options": [{"label": o.label, "count": o.count, "area": o.area} for o in vote.options],
        }, sort_keys=True)
        result_hash = "0x" + hashlib.sha256(hash_data.encode()).hexdigest()[:16]

        return result_str, summary, result_hash
