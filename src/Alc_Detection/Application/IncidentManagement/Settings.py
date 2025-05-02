class Settings:
    def __init__(self,
                 faces_count: int
    ):
        self._faces_count = faces_count
        
    @property
    def FACES_COUNT(self):
        return self._faces_count
    
    