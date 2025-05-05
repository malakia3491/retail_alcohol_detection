from uuid import UUID
from pydantic import BaseModel, HttpUrl
from datetime import datetime, time
from typing import Dict, List, Optional

class ScheduleDay(BaseModel):
    id: Optional[UUID] = None
    schedule_id: Optional[UUID] = None
    date_day: datetime

class Schedule(BaseModel):
    id: Optional[UUID] = None
    store_shift_id: Optional[UUID] = None
    holidays: List[ScheduleDay]
    write_day: datetime
    date_from: datetime
    date_to: datetime

class Shift(BaseModel):
    id: Optional[UUID] = None
    store_id: UUID
    schedule: Optional[Schedule] = None
    work_time_start: time
    work_time_end: time
    break_time_start: time
    break_time_end: time
    name: str
    staff_positions: dict[UUID, int]    

class Permition(BaseModel):
    id: Optional[UUID] = None
    name: str

class Post(BaseModel):
    id: Optional[UUID] = None
    name: str
    permitions: List[UUID]
    
class CalibrationBox(BaseModel):
    xyxy: List[int]
    conf: float

    def __eq__(self, other):
        return (
            self.xyxy == other.xyxy 
            and self.conf == other.conf
        )
    
    def __hash__(self):
        return hash((tuple(self.xyxy), self.conf))

class Store(BaseModel):
    id: Optional[UUID] = None
    name: str

class Product(BaseModel):
    id: Optional[UUID] = None
    image_url: Optional[str] = None 
    name: str

class PlanogramProduct(BaseModel):
    id: Optional[UUID] = None     
    product: Optional[Product] = None
    product_id: UUID
    count: int

class ProductBox(BaseModel):
    id: Optional[UUID] = None
    product_id: UUID
    planogram_product: Optional[PlanogramProduct] = None
    pos_x: int
    is_empty: bool

class Shelf(BaseModel):
    position: int
    product_boxes: List[ProductBox]

class ProductMatrix(BaseModel):
    products: List[PlanogramProduct]
    shelfs: List[Shelf]
        
class Person(BaseModel):
    id: Optional[UUID] = None
    telegram_id: Optional[str] = None
    name: str
    is_store_worker: Optional[bool] = None
    post: Optional[Post] = None
    shift_id: Optional[UUID] = None
    store_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    access_token: Optional[str] = None

class Shelving(BaseModel):
    id: Optional[UUID] = None
    shelves_count: int
    name: str

class Planogram(BaseModel):
    id: Optional[UUID] = None
    author: Person
    shelving: Shelving
    create_date: datetime
    product_matrix: ProductMatrix
    approver: Optional[Person]
    approval_date: Optional[datetime]

class PlanogramOrder(BaseModel):
    id: Optional[UUID] = None
    author: Person
    shelving_assignments: Dict[UUID, List[Planogram]]  
    create_date: datetime
    develop_date: datetime
    implementation_date: datetime
    shelvings: List[Shelving]
    is_declined: bool
    status: Optional[str] = None
    
class PlanogramOrdersResponse(BaseModel):
    planogram_orders: List[PlanogramOrder]
    
class CalibrationBoxesResponse(BaseModel):
    calibration_boxes: List[CalibrationBox]
    
class PlanogramOrdersPageResponse(BaseModel):
    planogram_orders: List[PlanogramOrder]
    total_count: int
    page: int
    
class ProductsResponse(BaseModel):
    products: List[Product]
    
class ShelvingsResponse(BaseModel):
    shelvings: List[Shelving]
    
class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID