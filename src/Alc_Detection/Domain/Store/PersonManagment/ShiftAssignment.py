from datetime import datetime


from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed    
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.StaffPosition import StaffPosition

class ShiftAssignment(IndexNotifiable):
    def __init__(
        self,
        assignment_date: datetime,
        assignments: dict[Person, StaffPosition],
        retail_id: str=None,
        id: str=None
    ):
        super().__init__()
        self._retail_id = retail_id
        self.id = id
        self._assignment_date = assignment_date
        self._assignments = assignments
   
    @indexed
    @property
    def retail_id(self) -> str:
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)
        
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