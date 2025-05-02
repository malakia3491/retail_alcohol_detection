from typing import Any, List, Optional, Union
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from Alc_Detection.Domain.Entities import PlanogramOrder
from Alc_Detection.Domain.Entities import Planogram
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase
from Alc_Detection.Persistance.Exceptions import ObjectNotFound, ObjectUpdateException
from Alc_Detection.Application.Mappers.PlanogramMapper import PlanogramMapper
from Alc_Detection.Application.Mappers.PlanogramOrderMapper import PlanogramOrderMapper
from Alc_Detection.Persistance.Models.Models import PlanogramOrder as PlanogramOrderModel
from Alc_Detection.Persistance.Models.ShelfDetection.ShelvingPlanogramOrder import ShelvingPlanogramOrder
from Alc_Detection.Persistance.Models.Models import Planogram as PlanogramModel

class PlanogramOrderRepository:
    def __init__(self,
                 planogram_order_mapper: PlanogramOrderMapper,
                 planogram_mapper: PlanogramMapper,
                 session_factory: AsyncSession,
                 cache: CacheBase):
        self.session_factory = session_factory
        self._planogram_order_mapper = planogram_order_mapper
        self._planogram_mapper = planogram_mapper
        self._cache = cache

    async def on_start(self):
        async with self.session_factory() as session:
            result = await session.execute(select(PlanogramOrderModel))
            [self._cache.put(row.id, self._planogram_order_mapper.map_to_domain_model(row)) for row in result.scalars().all()]
    
    async def get_all(self) -> list[PlanogramOrder]:
        return self._cache.get_all()
    
    async def get_last_order(self) -> PlanogramOrder:
        if len(self._cache) == 0:
            return None        
        orders = self._cache.get_all()
        orders = sorted(orders, key= lambda order: order.create_date)
        return orders[0]
    
    async def get_not_resolved_orders(self) -> list[PlanogramOrder]:
        if len(self._cache) == 0:
            return []
        orders = []        
        for order in self._cache.get_all():
            if not (order.is_resolved or order.is_declined):
                orders.append(order)
        return orders
    
    async def get_resolved_orders(self) -> list[PlanogramOrder]:
        if len(self._cache) == 0:
            return []
        orders = []        
        for order in self._cache.get_all():
            if order.is_resolved and not order.is_declined:
                orders.append(order)
        return orders   
            
    async def add_planogram(
        self,
        order_id: UUID,
        new_planogram: Planogram
    ):
        assignment = await self.get_shelving_assignment(new_planogram.shelving.id, order_id)
        order: PlanogramOrder = self._cache.get(order_id)
        planogram = self._planogram_mapper.map_to_db_model(domain_model=new_planogram,
                                                           assignment_id=assignment.id)
        async with self.session_factory() as session:
            session.add(planogram)                
            await session.commit()
            await session.refresh(planogram)
        new_planogram.id = planogram.id
        order.add_planogram(shelving=new_planogram.shelving, planogram=new_planogram)  
            
    async def update_planogram(
        self,
        order_id: UUID,
        planogram_id: UUID,
        data: dict[str, Any]
    ) -> int:
        obj = self._cache.get(order_id)
        if obj:
            try:
                async with self.session_factory() as session:
                    stmt = (
                        update(PlanogramModel)
                        .where(PlanogramModel.id == planogram_id)
                        .values(data)
                    )                    
                    await session.execute(stmt)
                    await session.commit()
            except Exception as ex:
                raise ex
        else:
            raise ObjectUpdateException(object_type=Planogram, object_id=planogram_id)
        return len([obj])
        
    async def get_shelving_assignment(self, shelving_id: UUID, order_id: UUID) -> ShelvingPlanogramOrder:
        try:
            async with self.session_factory() as session:
                stmt = (select(ShelvingPlanogramOrder).where(
                        (ShelvingPlanogramOrder.shelving_id == shelving_id) &
                        (ShelvingPlanogramOrder.planogram_order_id == order_id)))
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except Exception as ex:
            raise ObjectNotFound(object_id=(shelving_id, order_id), object_type=ShelvingPlanogramOrder)
        
    async def get(self, *ids: UUID) -> PlanogramOrder | List[PlanogramOrder]:
        in_cache_ids, not_in_cache_ids = self._cache.in_cache(*ids)
        objs = [self._cache.get(id) for id in in_cache_ids]
        if len(not_in_cache_ids) == 0: 
            if len(objs) == 1: return objs[0]
            else: return objs
        else: 
            async with self.session_factory() as session:
                try:
                    stm_result = await session.execute(select(PlanogramOrderModel).where(PlanogramOrderModel.id.in_(not_in_cache_ids)))
                    db_objs = [self._planogram_order_mapper.map_to_domain_model(model) for model in stm_result.scalars().all()]
                    for db_obj in db_objs:
                        self._cache.put(db_obj.id, db_obj)
                        objs.append(db_obj)
                except NoResultFound as ex:
                    raise ValueError(f"Записи с айди {not_in_cache_ids} не найдены")
        if len(objs) == 1: return objs[0]
        else: return objs
    
    async def add(self, *new_objs: PlanogramOrder) -> int:
        objs = []
        for new_obj in new_objs:                
            objs.append(self._planogram_order_mapper.map_to_db_model(new_obj))
            
        if len(objs) == 0: return 0
        async with self.session_factory() as session:
            session.add_all(objs)
            await session.commit()
            for obj in objs: await session.refresh(obj)  
        for obj in objs:
            self._cache.put(obj.id, self._planogram_order_mapper.map_to_domain_model(obj))
        return len(objs)