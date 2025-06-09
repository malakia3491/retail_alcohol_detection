from uuid import UUID
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

from Alc_Detection.Application.Requests.person_management import Person
from Alc_Detection.Application.Requests.retail import Product, Shelving

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
    
class Planogram(BaseModel):
    id: Optional[UUID] = None
    order_id: Optional[UUID] = None
    author: Person
    shelving: Shelving
    create_date: datetime
    product_matrix: ProductMatrix
    approver: Optional[Person]
    approval_date: Optional[datetime]
    
class Realogram(BaseModel):
    id: Optional[UUID]
    planogram_id: UUID
    shelving_id: UUID
    create_date: datetime
    img_src: str
    product_matrix: ProductMatrix
    accordance: float
    empties_count: int
    
class PlanogramOrder(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    author: Person
    shelving_assignments: Dict[UUID, List[Planogram]]  
    create_date: datetime
    develop_date: datetime
    implementation_date: datetime
    shelvings: List[Shelving]
    is_declined: bool
    status: Optional[str] = None