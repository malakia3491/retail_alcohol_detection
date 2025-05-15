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
    staff_positions: Optional[dict[UUID, int]] = None    

class Permition(BaseModel):
    id: Optional[UUID] = None
    name: str

class Post(BaseModel):
    id: Optional[UUID] = None
    name: str
    permitions: List[Permition]
    
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
    is_office: bool

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
    cords: Optional[List[float]] = None
    pos_x: int
    is_empty: bool
    is_incorrect_position: bool

class Shelf(BaseModel):
    position: int
    product_boxes: List[ProductBox]

class ProductMatrix(BaseModel):
    products: List[PlanogramProduct]
    shelfs: List[Shelf]
        
class Person(BaseModel):
    id: Optional[UUID] = None
    telegram_id: Optional[str] = None
    email: str
    name: str
    is_store_worker: Optional[bool] = None
    post: Optional[Post] = None
    shift: Optional[Shift] = None
    store: Optional[Store] = None
    is_active: Optional[bool] = None
    access_token: Optional[str] = None

class Shelving(BaseModel):
    id: Optional[UUID] = None
    shelves_count: int
    name: str

class Planogram(BaseModel):
    id: Optional[UUID] = None
    order_id: Optional[UUID] = None
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

class PlanogramDataResponse(BaseModel):
    shelving_id: UUID
    planogram_id: UUID
    order_id: UUID

class PlanogramsResponse(BaseModel):
    planogram_data: List[PlanogramDataResponse]
    
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
    
class Realogram(BaseModel):
    id: Optional[UUID]
    planogram_id: UUID
    shelving_id: UUID
    create_date: datetime
    img_src: str
    product_matrix: ProductMatrix
    accordance: float
    empties_count: int
    
class RealogramsPageResponse(BaseModel):
    realograms: List[Realogram]
    total_count: int
    page: int

class StoresResponse(BaseModel):
    stores: List[Store]

class RealogramsResponse(BaseModel):
    realograms: List[Realogram]
    
class PlanogramComplianceReportRow(BaseModel):
    total_notifications_empty: int
    total_notifications_mismatch: int
    resolved_on_time_empty: int
    resolved_on_time_mismatch: int
    unresolved_empty_no_stock: int
    avg_reaction_time_empty_min: Optional[float] 
    avg_reaction_time_mismatch_min: Optional[float]
    avg_planogram_accordance_percent: Optional[float]                    

class PlanogramComplianceReport(BaseModel):
    rows: Dict[str, Dict[str, PlanogramComplianceReportRow]]
    
class PlanogramUsageReportRow(BaseModel):
    planogram_date: datetime
    store_name: str
    approval_date: datetime
    approver_name: str
    calibration_date: datetime
    calibrator_name: str
    avg_accordance_percent: float
    count: int

class PlanogramUsageReport(BaseModel):
    rows: Dict[str, Dict[str, Dict[str, PlanogramUsageReportRow]]]