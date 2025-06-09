from uuid import UUID

from Alc_Detection.Domain.Store.PersonManagment.Permition import Permition
from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed    

class Post(IndexNotifiable):
    def __init__(
        self,
        name: str,
        permitions: list[Permition]=[],
        retail_id: str=None,
        id: UUID=None
    ):
        super().__init__() 
        self._retail_id = retail_id
        self.id = id
        self.name = name
        self._permitions = permitions
    
    @indexed
    @property
    def retail_id(self) -> str:
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)     
    
    @property
    def permitions(self) -> list[Permition]:
        return self._permitions
    
    def is_allowed(self, *permitions: Permition) -> bool:
        for permition in permitions:
            if not permition in self._permitions:
                return True
        return False             
        
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return self.__str__()           
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Post):
            return False
        return self.name == other.name
    
    def __hash__(self):
        return hash(self.name)