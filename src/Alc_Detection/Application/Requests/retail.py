from uuid import UUID
from pydantic import BaseModel
from typing import  Optional

class Store(BaseModel):
    id: Optional[UUID] = None
    name: str
    is_office: bool

class Product(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    image_url: Optional[str] = None 
    name: str

class Shelving(BaseModel):
    id: Optional[UUID] = None
    retail_id: Optional[str] = None
    shelves_count: int
    name: str