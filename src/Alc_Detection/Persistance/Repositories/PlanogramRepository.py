import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from torch import select

from Alc_Detection.Domain import ProductMatrix
from Alc_Detection.Persistance.Models.Models import *

class PlanogramRepository:
    
    def __init__(self,
                 session_factory: AsyncSession):
        self.session_factory = session_factory
        
    async def get_actual_planogram(self,
                                   store_id: UUID,
                                   shelving_id: UUID) -> ProductMatrix:
        async with self.session_factory() as session:
            async with session.begin():
                result = await session.execute(select(Planogram).where(Planogram.store_id == store_id and Planogram.shelving_id == shelving_id))
                db_planogram = result.scalars().first()
                
                return db_planogram
        
    async def set_planogram(self,
                            shelving_id: str,
                            planogram_matrix: ProductMatrix,
                            approval_date: datetime) -> None:
        pass