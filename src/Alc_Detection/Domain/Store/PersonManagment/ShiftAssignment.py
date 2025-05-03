from datetime import datetime

from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Post import Post

class ShiftAssignment:
    def __init__(
        self,
        assignment_date: datetime,
        asignments: dict[Person, Post],
        id: str=None
    ):
        self.id = id
        self._assignment_date = assignment_date
        self._assignments = asignments
        
    @property
    def date(self):
        return self._assignment_date
    
    @property
    def assignments(self):
        return self._assignments
    
    def person_post(self, person: Person) -> Post:
        if person in self._assignments:
            return self._assignments[person]
        return None