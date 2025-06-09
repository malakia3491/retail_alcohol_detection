from typing import List

from video_control.domain.Shelving import Shelving
from video_control.persistance.cache import CacheBase

class ShelvingRepository:
    def __init__(self,
                 cache: CacheBase):
        self._cache = cache
        
    async def on_start(self, items: list[Shelving] = None) -> 'ShelvingRepository':
        for item in items:
            self._cache.put(item.id, item)
        return self

    @property
    def is_filled(self) -> bool:
        return len(self._cache) > 0
              
    async def load(self, shelvings: list[Shelving]):
        self._cache.clear()
        for shelving in shelvings:
            self._cache.put(shelving.id, shelving)
    
    async def get_all(self) -> list[Shelving]:
        return self._cache.get_all()
    
    async def get(self, *ids: str) -> Shelving | List[Shelving]:
        in_cache_ids, not_in_cache_ids = self._cache.in_cache(*ids)
        objs = [self._cache.get(id) for id in in_cache_ids]
        if len(not_in_cache_ids) == 0:
            if len(objs) == 1: return objs[0]
            else: return objs
        if len(objs) == 1: return objs[0]
        else: return objs
    
    async def add(self, shelving: Shelving) -> None:
        """
        Add a new Videocamera to the repository.
        
        :param videocamera: The Videocamera object to add.
        """
        self._cache.put(shelving.id, shelving)