class Settings:
    def __init__(self,
                 faces_count: int,
                 need_creation_time: float
    ):
        self._faces_count = faces_count
        self._need_creation_time = need_creation_time
        
    @property
    def FACES_COUNT(self) -> int:
        return self._faces_count
    
    @property
    def REACTION_TIME(self) -> float:
        return self._need_creation_time