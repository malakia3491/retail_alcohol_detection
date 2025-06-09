from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, time
from typing import List, Optional

from Alc_Detection.Application.Requests.retail import Store

class ScheduleDay(BaseModel):
    id: Optional[UUID] = None
    schedule_id: Optional[UUID] = None
    date_day: datetime

class Schedule(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    store_shift_id: Optional[UUID] = None
    holidays: List[ScheduleDay]
    write_day: datetime
    date_from: datetime
    date_to: datetime

class Shift(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    store_id: UUID
    retail_store_id: Optional[str] = None
    schedule: Optional[Schedule] = None
    work_time_start: time
    work_time_end: time
    break_time_start: time
    break_time_end: time
    name: str
    staff_positions: Optional[dict[UUID, int]] = None    

class Permition(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    name: str

class Post(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    name: str
    permitions: List[Permition]
        
class Person(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    telegram_id: Optional[str] = None
    email: str
    name: str
    is_store_worker: Optional[bool] = None
    post: Optional[Post] = None
    shift: Optional[Shift] = None
    store: Optional[Store] = None
    is_active: Optional[bool] = None
    access_token: Optional[str] = None
    
class ShiftAssignment(BaseModel):
    id: Optional[str]
    date: datetime