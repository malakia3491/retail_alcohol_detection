from uuid import UUID

class Post:
    def __init__(
        self,
        name: str,
        is_regular: bool,
        is_administrative: bool,
        id: UUID=None
    ): 
        self.id = id
        self.name = name
        self.is_regular = is_regular
        self.is_administrative = is_administrative
        
    def __str__(self) -> str:
        return self.name
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Post):
            return False
        return self.name == other.name