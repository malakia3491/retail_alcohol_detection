from datetime import datetime, time
from pydantic import BaseModel
from typing import List
 
class Permition(BaseModel):
    id: str
    name: str

class Product(BaseModel):
    id: str
    name: str

class Shelving(BaseModel):
    id: str
    shelves_count: int
    name: str 
 
class Post(BaseModel):
    id: str
    name: str

class Person(BaseModel):
    id: str
    email: str
    name: str
    is_store_worker: bool
    is_active: bool

class Schedule(BaseModel):
    id: str
    holidays: List[datetime]
    write_day: datetime
    date_from: datetime
    date_to: datetime

class StaffPosition(BaseModel):
    id: str
    post: Post
    count: int

class Assignment(BaseModel):
    person: Person
    position: StaffPosition

class ShiftAssignment(BaseModel):
    id: str
    date: datetime
    workers: List[Assignment]
    
class Shift(BaseModel):
    id: str
    schedule: List[Schedule]
    work_time_start: time
    work_time_end: time
    break_time_start: time
    break_time_end: time
    name: str
    staff_positions: List[StaffPosition]
    shift_assignments: List[ShiftAssignment]
     
class Store(BaseModel):
    id: str
    name: str
    is_office: bool
    shifts: List[Shift]

class AddDataRequest(BaseModel):
    shelvings: List[Shelving]
    stores: List[Store]
    persons: List[Person]
    products: List[Product]
    posts: List[Post]