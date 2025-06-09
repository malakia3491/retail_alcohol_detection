from typing import List, Optional

from video_control.domain.Shelving import Shelving
from video_control.domain.Videocamera import Videocamera
from video_control.persistance.cache import CacheBase
from video_control.persistance.store.JsonStore import JsonStore

class VideocameraRepository:
    def __init__(self,
                 json_store: JsonStore,
                 cache: CacheBase):
        self._cache = cache
        self._json_store = json_store
        
    async def on_start(self) -> 'VideocameraRepository':
        data = self._json_store.load()        
        for item in data:
            shelving_data = item.get('shelving')
            shelving: Optional[Shelving] = None
            if shelving_data is not None:
                shelving = Shelving(
                    id=shelving_data['id'],
                    name=shelving_data['name']
                )
            cam = Videocamera(
                ip=item['ip'],                
                port=item['port'],
                url=item['url'],
                username=item['username'],
                password=item['password'],
                shelving=shelving
            )
            self._cache.put(cam.id, cam)
        print('VideocameraRepository: loaded from JSON store')
        return self
            
    @property
    def is_filled(self) -> bool:
        return len(self._cache) > 0
    
    async def load(self, videocameras: list[Videocamera]):
        self._cache.clear()
        for videocamera in videocameras:
            self._cache.put(videocamera.id, videocamera)
        await self.save() 
    
    async def get_all(self) -> list[Videocamera]:
        return self._cache.get_all()
    
    async def get(self, *ids: str) -> Videocamera | List[Videocamera]:
        in_cache_ids, not_in_cache_ids = self._cache.in_cache(*ids)
        objs = [self._cache.get(id) for id in in_cache_ids]
        if len(not_in_cache_ids) == 0:
            if len(objs) == 1: return objs[0]
            else: return objs
        if len(objs) == 1: return objs[0]
        else: return objs
    
    async def add(self, videocamera: Videocamera) -> None:
        """
        Add a new Videocamera to the repository.
        
        :param videocamera: The Videocamera object to add.
        """
        self._cache.put(videocamera.id, videocamera)
        
    async def remove(self, videocamera: Videocamera) -> None:
        """
        Remove a Videocamera from the repository.
        
        :param videocamera: The Videocamera object to remove.
        """
        self._cache.remove(videocamera.id)    
        
    async def save(self) -> None:
        self._json_store.save([cam.to_dict() for cam in self._cache.get_all()])