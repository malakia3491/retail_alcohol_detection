from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List 
from sqlalchemy.exc import NoResultFound

from Alc_Detection.Domain.Store.PersonManagment.Permition import Permition
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Persistance.Exceptions import ObjectNotFound
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase
from Alc_Detection.Persistance.Models.Models import Permition as PermitionModel

class PermitionRepository:
    def __init__(self, 
                 session_factory: AsyncSession,
                 cache: CacheBase):
        self.session_factory = session_factory
        self._cache = cache

    async def on_start(self):
        async with self.session_factory() as session:                
            result = await session.execute(select(PermitionModel))
            for row in result.scalars().all():
                permition = Permition(id=row.id, name=row.name)        
                self._cache.put(row.id, permition)

    async def get_all(self) -> list[Permition]:
        return self._cache.get_all()    
    
    async def get(self, *ids: UUID) -> Permition | List[Permition]:
        in_cache_ids, not_in_cache_ids = self._cache.in_cache(*ids)
        objs = [self._cache.get(id) for id in in_cache_ids]
        if len(not_in_cache_ids) == 0: 
            if len(objs) == 1: return objs[0]
            else: return objs
        else: 
            async with self.session_factory() as session:
                try:
                    stm_result = await session.execute(select(PermitionModel).where(PermitionModel.id.in_(not_in_cache_ids)))
                    db_objs = [Permition(id=model.id, name=model.name) for model in stm_result.scalars().all()]
                    for db_obj in db_objs:
                        self._cache.put(db_obj.id, db_obj)
                        objs.append(db_obj)
                except NoResultFound as ex:
                    raise ValueError(f"Записи с айди {not_in_cache_ids} не найдены")
        if len(objs) == 1: return objs[0]
        else: return objs
    
    async def add(self, *new_objs: Permition) -> int:
        objs = []
        for new_obj in new_objs:                
            if self._cache.contains(new_obj): continue
            objs.append(PermitionModel(name=new_obj.name))
            
        if len(objs) == 0: return 0
        async with self.session_factory() as session:
            session.add_all(objs)
            await session.commit()
            for obj in objs: await session.refresh(obj)  
        for obj in objs:
            self._cache.put(obj.id, Permition(id=obj.id, name=obj.name))
        return len(objs)