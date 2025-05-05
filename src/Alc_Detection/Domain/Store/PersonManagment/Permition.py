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