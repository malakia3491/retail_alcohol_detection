from uuid import UUID

class Permition:
    def __init__(
        self,
        name: str,
        id: UUID=None
    ):
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