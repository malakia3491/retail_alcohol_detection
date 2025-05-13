from datetime import datetime

from Alc_Detection.Domain.RetailModel import RetailModel
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.StaffPosition import StaffPosition

class ShiftAssignment(RetailModel):
    def __init__(
        self,
        assignment_date: datetime,
        assignments: dict[Person, StaffPosition],
        retail_id: str=None,
        id: str=None
    ):
        super().__init__(retail_id=retail_id)
        self.id = id
        self._assignment_date = assignment_date
        self._assignments = assignments
        
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