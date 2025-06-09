from uuid import UUID
from pydantic import BaseModel
from typing import List

from Alc_Detection.Application.Requests.retail import  Product, Shelving, Store
from Alc_Detection.Application.Requests.detection import PlanogramOrder, CalibrationBox, Realogram

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

class RealogramsPageResponse(BaseModel):
    realograms: List[Realogram]
    total_count: int
    page: int

class StoresResponse(BaseModel):
    stores: List[Store]

class RealogramsResponse(BaseModel):
    realograms: List[Realogram]