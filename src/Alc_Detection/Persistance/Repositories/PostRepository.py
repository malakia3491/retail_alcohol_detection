from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List 
from sqlalchemy.exc import NoResultFound

from Alc_Detection.Application.Mappers.PostMapper import PostMapper
from Alc_Detection.Domain.Entities import Product
from Alc_Detection.Persistance.Exceptions import ObjectNotFound
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase
from Alc_Detection.Persistance.Models.Models import Post as PostModel

class PostRepository:
    def __init__(self, 
                 session_factory: AsyncSession,
                 cache: CacheBase,
                 post_mapper: PostMapper):
        self.session_factory = session_factory
        self._post_mapper = post_mapper
        self._cache = cache

    async def on_start(self):
        async with self.session_factory() as session:                
            result = await session.execute(select(PostModel))
            for row in result.scalars().all():
                post = self._post_mapper.map_to_domain_model(row)          
                self._cache.put(row.id, post)

    async def get_all(self) -> list[Product]:
        return self._cache.get_all()    
    
    async def get(self, *ids: UUID) -> Product | List[Product]:
        raise NotImplementedError("Метод не реализован")
        in_cache_ids, not_in_cache_ids = self._cache.in_cache(*ids)
        objs = [self._cache.get(id) for id in in_cache_ids]
        if len(not_in_cache_ids) == 0: 
            if len(objs) == 1: return objs[0]
            else: return objs
        else: 
            async with self.session_factory() as session:
                try:
                    stm_result = await session.execute(select(PostModel).where(PostModel.id.in_(not_in_cache_ids)))
                    db_objs = [self._post_mapper.map_to_domain_model(model) for model in stm_result.scalars().all()]
                    for db_obj in db_objs:
                        self._cache.put(db_obj.id, db_obj)
                        objs.append(db_obj)
                except NoResultFound as ex:
                    raise ValueError(f"Записи с айди {not_in_cache_ids} не найдены")
        if len(objs) == 1: return objs[0]
        else: return objs
    
    async def add(self, *new_objs: Product) -> int:
        raise NotImplementedError("Метод не реализован")
        objs = []
        for new_obj in new_objs:                
            if self._cache.contains(new_obj): continue
            objs.append(self._post_mapper.map_to_db_model(new_obj))
            
        if len(objs) == 0: return 0
        async with self.session_factory() as session:
            session.add_all(objs)
            await session.commit()
            for obj in objs: await session.refresh(obj)  
        for obj in objs:
            self._cache.put(obj.id, self._product_mapper.map_to_domain_model(obj))
        return len(objs)