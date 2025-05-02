from datetime import datetime

class Schedule:
    def __init__(
        self,
        holidays: list[datetime]
    ):
        self._holidayes = holidays                
        
    def contains(self, date: datetime):
        return date in self._holidayes