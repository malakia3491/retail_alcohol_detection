from uuid import UUID

from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed
from Alc_Detection.Domain.Store.PersonManagment.Post import Post

class StaffPosition(IndexNotifiable):
    def __init__(
        self,
        post: Post,
        count: int,
        retail_id: str=None,
        id: UUID=None
    ):
        super().__init__()
        self.id = id
        self._retail_id = retail_id
        self.post = post
        self.count = count 

    @indexed
    @property
    def retail_id(self) -> str:
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)
        
    def __eq__(self, value):
        return isinstance(value, 'StaffPosition') and \
               self.post == value.post and \
               self.count == value.count
               
    def __str__(self):
        return f"StaffPosition({self.post}):, {self.count}"
               
    def __repr__(self) -> str:
        return self.__str__()               
               
    def __hash__(self):
        return hash((self.post, self.count))