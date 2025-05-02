from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from Alc_Detection.Application.Requests.Models import Product, ProductMatrix, Store, Shelving, Person, CalibrationBox
    
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
    is_worker: Optional[bool] = None
    
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