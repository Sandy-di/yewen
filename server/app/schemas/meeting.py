"""会议相关 Schema"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class MeetingAttendeeOut(BaseModel):
    id: str
    userId: str
    rsvpStatus: str = "pending"
    checkedIn: bool = False
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class MeetingMinutesOut(BaseModel):
    id: str
    content: str = ""
    recordingUrl: str = ""
    isFinal: bool = False
    createdBy: Optional[str] = None
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class MeetingListOut(BaseModel):
    meetingId: str
    title: str
    meetingType: str
    location: str = ""
    scheduledAt: Optional[datetime] = None
    status: str
    attendeeCount: int = 0
    checkedInCount: int = 0
    createdAt: Optional[datetime] = None

    class Config:
        from_attributes = True


class MeetingDetailOut(MeetingListOut):
    description: str = ""
    attendees: List[MeetingAttendeeOut] = []
    minutes: List[MeetingMinutesOut] = []


class MeetingCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field("", max_length=5000)
    meetingType: str = Field("committee", pattern="^(committee|owner_assembly)$")
    location: str = Field("", max_length=200)
    scheduledAt: Optional[datetime] = None
    attendeeIds: List[str] = Field([], description="参会人用户ID列表")


class MeetingMinutesCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=10000)
    recordingUrl: str = Field("", max_length=500)
    isFinal: bool = False


class MeetingCheckIn(BaseModel):
    userId: str


class MeetingRsvp(BaseModel):
    rsvpStatus: str = Field(..., pattern="^(confirmed|declined)$")
