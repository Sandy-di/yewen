"""会议服务 — CRUD + 签到 + 纪要"""

from datetime import datetime, timezone
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Meeting, MeetingAttendee, MeetingMinutes, User
from app.schemas.meeting import MeetingCreate
from app.utils.logger import get_logger

logger = get_logger("meeting_service")


class MeetingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_list(self, community_id: str, *, status: str | None = None, page: int = 1, page_size: int = 20):
        query = select(Meeting).where(Meeting.community_id == community_id)
        count_query = select(func.count(Meeting.id)).where(Meeting.community_id == community_id)

        if status and status != "all":
            query = query.where(Meeting.status == status)
            count_query = count_query.where(Meeting.status == status)

        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        query = query.order_by(Meeting.scheduled_at.desc() if Meeting.scheduled_at else Meeting.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        items = result.scalars().all()
        return items, total

    async def get_by_id(self, meeting_id: str) -> Meeting | None:
        result = await self.db.execute(select(Meeting).where(Meeting.id == meeting_id))
        return result.scalar_one_or_none()

    async def create(self, user: User, data: MeetingCreate) -> Meeting:
        meeting = Meeting(
            community_id=user.community_id,
            title=data.title,
            description=data.description,
            meeting_type=data.meetingType,
            location=data.location,
            scheduled_at=data.scheduledAt,
            status="scheduled",
            created_by=user.id,
        )
        self.db.add(meeting)
        await self.db.flush()

        # 添加参会人
        for uid in data.attendeeIds:
            attendee = MeetingAttendee(meeting_id=meeting.id, user_id=uid, rsvp_status="pending")
            self.db.add(attendee)

        await self.db.flush()
        logger.info(f"会议创建: {meeting.id}")
        return meeting

    async def check_in(self, meeting_id: str, user_id: str) -> None:
        result = await self.db.execute(
            select(MeetingAttendee).where(
                MeetingAttendee.meeting_id == meeting_id,
                MeetingAttendee.user_id == user_id,
            )
        )
        attendee = result.scalar_one_or_none()
        if not attendee:
            # 自动添加并签到
            attendee = MeetingAttendee(meeting_id=meeting_id, user_id=user_id, rsvp_status="confirmed")
            self.db.add(attendee)
            await self.db.flush()
        attendee.checked_in = True
        attendee.checked_in_at = datetime.now(timezone.utc)
        self.db.add(attendee)
        await self.db.flush()

    async def rsvp(self, meeting_id: str, user_id: str, rsvp_status: str) -> None:
        result = await self.db.execute(
            select(MeetingAttendee).where(
                MeetingAttendee.meeting_id == meeting_id,
                MeetingAttendee.user_id == user_id,
            )
        )
        attendee = result.scalar_one_or_none()
        if not attendee:
            attendee = MeetingAttendee(meeting_id=meeting_id, user_id=user_id)
            self.db.add(attendee)
            await self.db.flush()
        attendee.rsvp_status = rsvp_status
        self.db.add(attendee)
        await self.db.flush()

    async def add_minutes(self, meeting_id: str, user_id: str, content: str, recording_url: str = "", is_final: bool = False) -> MeetingMinutes:
        minutes = MeetingMinutes(
            meeting_id=meeting_id,
            content=content,
            recording_url=recording_url,
            is_final=is_final,
            created_by=user_id,
        )
        self.db.add(minutes)
        await self.db.flush()
        return minutes

    async def update_status(self, meeting_id: str, status: str) -> None:
        meeting = await self.get_by_id(meeting_id)
        if not meeting:
            raise ValueError("会议不存在")
        meeting.status = status
        self.db.add(meeting)
        await self.db.flush()
