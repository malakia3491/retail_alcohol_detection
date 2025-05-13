import uuid
from sqlalchemy import Column, String

from Alc_Detection.Persistance.Models.BaseModel import BaseModel
  
class BaseStoreModel(BaseModel): 
    __abstract__ = True

    retail_id = Column(String, unique=True)