from uuid import UUID

class Post:
    def __init__(
        self,
        name: str,
        id: UUID=None
    ): 
        self.id = id
        self.name = name