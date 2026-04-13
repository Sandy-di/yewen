"""会议路由 — CRUD + 签到 + 纪要"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.models import User, Meeting
from app.middleware.auth import get_current_user, require_role
from app.schemas.meeting import (
    MeetingListOut, MeetingDetailOut, MeetingAttendeeOut, MeetingMinutesOut,
    MeetingCreate, MeetingMinutesCreate, MeetingCheckIn, MeetingRsvp,
)
from app.services.meeting_service import MeetingService

router = APIRouter()


def meeting_to_list_out(m: Meeting) -> MeetingListOut:
    return MeetingListOut(
        meetingId=m.id,
        title=m.title,
        meetingType=m.meeting_type,
        location=m.location,
        scheduledAt=m.scheduled_at,
        status=m.status,
        attendeeCount=len(m.attendees) if m.attendees else 0,
        checkedInCount=sum(1 for a in (m.attendees or []) if a.checked_in),
        createdAt=m.created_at,
    )


@router.get("", response_model=dict)
async def get_meeting_list(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    meetings, total = await service.get_list(
        current_user.community_id, status=status, page=page, page_size=pageSize
    )
    outs = [meeting_to_list_out(m).model_dump() for m in meetings]
    return {"data": outs, "total": total, "page": page, "pageSize": pageSize}


@router.get("/{meeting_id}", response_model=MeetingDetailOut)
async def get_meeting_detail(
    meeting_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    meeting = await service.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="会议不存在")

    base = meeting_to_list_out(meeting)
    attendees = [
        MeetingAttendeeOut(id=a.id, userId=a.user_id, rsvpStatus=a.rsvp_status, checkedIn=a.checked_in, createdAt=a.created_at)
        for a in (meeting.attendees or [])
    ]
    minutes = [
        MeetingMinutesOut(id=m.id, content=m.content, recordingUrl=m.recording_url, isFinal=m.is_final, createdBy=m.created_by, createdAt=m.created_at)
        for m in (meeting.minutes or [])
    ]

    return MeetingDetailOut(
        **base.model_dump(),
        description=meeting.description,
        attendees=attendees,
        minutes=minutes,
    )


@router.post("")
async def create_meeting(
    req: MeetingCreate,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    meeting = await service.create(current_user, req)
    return {"success": True, "meetingId": meeting.id}


@router.post("/{meeting_id}/check-in")
async def check_in_meeting(
    meeting_id: str,
    req: MeetingCheckIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    await service.check_in(meeting_id, req.userId)
    return {"success": True}


@router.post("/{meeting_id}/rsvp")
async def rsvp_meeting(
    meeting_id: str,
    req: MeetingRsvp,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    await service.rsvp(meeting_id, current_user.id, req.rsvpStatus)
    return {"success": True}


@router.post("/{meeting_id}/minutes")
async def add_meeting_minutes(
    meeting_id: str,
    req: MeetingMinutesCreate,
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    await service.add_minutes(meeting_id, current_user.id, req.content, req.recordingUrl, req.isFinal)
    return {"success": True}


@router.put("/{meeting_id}/status")
async def update_meeting_status(
    meeting_id: str,
    status: str = Query(..., pattern="^(ongoing|ended|cancelled)$"),
    current_user: User = Depends(require_role("committee")),
    db: AsyncSession = Depends(get_db),
):
    service = MeetingService(db)
    try:
        await service.update_status(meeting_id, status)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"success": True}
