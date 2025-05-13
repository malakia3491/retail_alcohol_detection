from uuid import UUID

from Alc_Detection.Domain.RetailModel import RetailModel

class Permition(RetailModel):
    def __init__(
        self,
        name: str,
        retail_id: str=None,
        id: UUID=None
    ):
        super().__init__(retail_id=retail_id)
        self._name = name
        self.id = id
        
    @property
    def name(self):
        return self._name
    
    def __eq__(self, value):
        return isinstance(value, Permition) and \
               self.name == value.name
               
    def __hash__(self):
        return hash(self.name)