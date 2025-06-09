from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from Alc_Detection.Application.Requests.detection import CalibrationBox, ProductMatrix
from Alc_Detection.Application.Requests.person_management import Permition, Person, Post, Schedule, Shift
from Alc_Detection.Application.Requests.retail import Product, Shelving, Store

    
class AddPlanogramRequest(BaseModel):
    order_id: UUID
    author_id: UUID
    shelving_id: UUID
    product_matrix: ProductMatrix
    
class UpdatePersonRequest(BaseModel):
    person_id: UUID
    telegram_id: Optional[str] = None
    store_id: Optional[UUID] = None
    name: Optional[str] = None
    is_store_worker: Optional[bool] = None
    
class ApprovePlanogramRequest(BaseModel):
    approver_id: UUID
    order_id: UUID
    planogram_id: UUID    
    
class DismissPersonRequest(BaseModel):
    person_id: UUID

class UpdatePersonsRequest(BaseModel):
    requests: List[UpdatePersonRequest]
    
class AddStoresRequest(BaseModel):
    stores: List[Store]

class AddProductsRequest(BaseModel):
    products: List[Product]
    
class AddShelvingsRequest(BaseModel):
    shelvings: List[Shelving]
    
class AddPersonsRequest(BaseModel):
    persons: List[Person]

class AddCalibrationBoxesRequest(BaseModel):
    order_id: UUID
    person_id: UUID
    shelving_id: UUID
    store_id: UUID
    calibration_boxes: List[CalibrationBox]
    
class AddPostsRequest(BaseModel):
    posts: List[Post]
    
class AddShiftsRequest(BaseModel):
    store_id: UUID
    shifts: List[Shift]
    
class AddScheduleRequest(BaseModel):
    store_id: UUID
    shift_id: UUID
    schedule: Schedule
    
class LoginRequest(BaseModel):
    login: str
    password: str
    
class AddPostsRequest(BaseModel):
    posts: list[Post]
    
class AddPermitionsRequest(BaseModel):
    permitions: list[Permition]
    
class StaffPositionAssignment(BaseModel):
    person_id: UUID
    post_id: UUID

class AddShiftAssignment(BaseModel):
    store_id: UUID
    shift_id: UUID
    assignments: List[StaffPositionAssignment]    