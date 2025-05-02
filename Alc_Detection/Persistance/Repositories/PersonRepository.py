from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy import bindparam
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Union, List, Optional
from sqlalchemy.exc import NoResultFound

from Alc_Detection.Domain.Entities import Person
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase
from Alc_Detection.Persistance.Exceptions import ObjectUpdateException
from Alc_Detection.Persistance.Models.Models import Person as PersonModel

class PersonRepository:
    def __init__(self, 
                 person_mapper: PersonMapper,
                 session_factory: AsyncSession,
                 cache: CacheBase):
        self.session_factory = session_factory
        self._person_mapper = person_mapper
        self._cache = cache
        
    async def on_start(self):
        async with self.session_factory() as session:
            result = await session.execute(select(PersonModel))
            [self._cache.put(row.id, self._person_mapper.map_to_domain_model(row)) for row in result.scalars().all()]
            
    async def get(self, *ids: UUID) -> Person | List[Person]:
        in_cache_ids, not_in_cache_ids = self._cache.in_cache(*ids)
        objs: list[Person] = [self._cache.get(id) for id in in_cache_ids]
        if len(not_in_cache_ids) == 0:
            if len(objs) == 1: return objs[0]
            else: return objs
        else: 
            async with self.session_factory() as session:
                try:
                    stm_result = await session.execute(select(PersonModel).where(PersonModel.id.in_(not_in_cache_ids)))
                    db_objs = [self._person_mapper.map_to_domain_model(model) for model in stm_result.scalars().all()]
                    for db_obj in db_objs:
                        self._cache.put(db_obj.id, db_obj)
                        objs.append(db_obj)
                except NoResultFound as ex:
                    raise ValueError(f"Записи с айди {not_in_cache_ids} не найдены")
        if len(objs) == 1: return objs[0]
        else: return objs
    
    async def add(self, *new_objs: Person) -> int:
        objs = []
        for new_obj in new_objs:
            if self._cache.contains(new_obj): continue                
            objs.append(self._person_mapper.map_to_db_model(new_obj))
            
        if len(objs) == 0: return 0
        async with self.session_factory() as session:
            session.add_all(objs)
            await session.commit()
            for obj in objs: await session.refresh(obj)  
        for obj in objs:
            self._cache.put(obj.id, self._person_mapper.map_to_domain_model(obj))
        return len(objs)
    
    async def update(self, obj_id: UUID, data: dict) -> int:        
        obj = self._cache.get(obj_id)
        if obj:
            for key in data:
                obj.__setattr__(str(key), data[key])
            try:
                async with self.session_factory() as session:
                    stmt = (
                        update(PersonModel)
                        .where(PersonModel.id == obj_id)
                        .values(data)
                    )
                    
                    await session.execute(stmt)
                    await session.commit()
            except Exception as ex:
                raise ex
        else:
            raise ObjectUpdateException(object_type=Person, object_id=obj_id)
        return len([obj])