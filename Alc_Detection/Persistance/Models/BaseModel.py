import uuid
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import  UUID, Column, DateTime, func
  
class BaseModel(DeclarativeBase): 
    __abstract__ = True

    id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now()) 
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())  