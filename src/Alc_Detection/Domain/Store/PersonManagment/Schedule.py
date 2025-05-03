from datetime import datetime

class Schedule:
    def __init__(
        self,
        date_assignment: datetime,
        holidays: list[datetime],
        id: str=None
    ):
        self.id = id
        self._date_assignment = date_assignment
        self._holidayes = holidays                

    @property
    def date_assignment(self):
        return self._date_assignment
            
    def contains(self, date: datetime):
        return date in self._holidayes