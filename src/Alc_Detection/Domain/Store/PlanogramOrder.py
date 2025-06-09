from datetime import datetime
from uuid import UUID  
from Alc_Detection.Domain.Exceptions.Exceptions import ApprovePlanogramInDeclinedOrder
from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed
from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.Shelving import Shelving

class PlanogramOrder(IndexNotifiable):
    def __init__(self,
                 author: Person,
                 create_date: datetime,
                 develop_date: datetime,
                 implementation_date: datetime,
                 is_declined: bool = False,
                 retail_id: str=None,
                 id: UUID = None,
                 shelvings: list[Shelving] = []):
        super().__init__()
        self.id = id
        self._retail_id = retail_id
        self.author = author
        self.shelving_assignments: dict[Shelving, list[Planogram]] = {}
        for shelving in shelvings:
            self.shelving_assignments[shelving] = [] 
        self.create_date = create_date
        self.develop_date = develop_date
        self._is_declined = is_declined
        self.implementation_date = implementation_date
    
    @indexed
    @property
    def retail_id(self) -> str:
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)
        
    def get_planogram(self,                      
                      planogram_id: UUID
    ) -> Planogram:
        for _, planograms in self.shelving_assignments.items():
            for planogram in planograms:
                if planogram.id == planogram_id:
                    return planogram
        return None
    
    @property
    def status(self) -> str:
        if self.is_declined:
            return "Отменён"
        if self.is_resolved:
            return "Согласован"
        return "В работе"
    
    @property
    def there_is_no_planograms(self) -> bool:
        for shelving, planograms in self.shelving_assignments.items():
            if len(planograms) != 0:
                return False
        return True
    
    def approve_planogram(self,
                          approver: Person,
                          date: datetime,
                          planogram_id: UUID
    ) -> None:
        if self.is_declined:
            raise ApprovePlanogramInDeclinedOrder(order_id=self.id)
        planogram = self.get_planogram(planogram_id)

        if not planogram is None and not self.is_resolved and not self.is_declined:
            planogram.approve(approval_date=date, approver=approver)         
        else:
             raise ValueError(planogram_id)
        
    def unapprove_planogram(self,
                            date: datetime,
                            planogram_id: UUID
    ) -> None:
        if self.is_declined:
            raise ApprovePlanogramInDeclinedOrder(order_id=self.id)
        planogram = self.get_planogram(planogram_id)
        if not planogram is None and date < self.develop_date:
            planogram.unapprove()         
        else:
            raise ValueError(planogram_id)   
    
    def get_agreed_planogram(self, shelving: Shelving) -> Planogram:
        if self.contains(shelving):
            for planogram in self.shelving_assignments[shelving]:
                if planogram.is_agreed():
                    return planogram
        return None 
                
    def add_shelving_assignment(self, shelving: Shelving):
        if self.contains(shelving):              
            raise ValueError(shelving)
        self.shelving_assignments[shelving] = []
        
    def add_planogram(self, shelving: Shelving, planogram: Planogram):
        if not self.contains(shelving):   
            raise ValueError(shelving)
        if planogram in self.shelving_assignments[shelving]:
            raise ValueError(planogram)
        self.shelving_assignments[shelving].append(planogram)
     
    def add_planograms(self, shelving: Shelving, planograms: list[Planogram]):
        if not self.contains(shelving):   
            raise ValueError(shelving)
        for planogram in planograms:
            if planogram in self.shelving_assignments[shelving]:
                raise ValueError(planogram)
            self.shelving_assignments[shelving].append(planogram)
            
    def fill_order(self, assignments: dict[Shelving, list[Planogram]]):
        for shelving, planograms in assignments.items():
            if not self.contains(shelving):   
                raise ValueError(shelving)
            self.add_planograms(shelving, planograms)
        
    def is_shelving_resolved(self, shelving: Shelving):
        if not self.contains(shelving):   
            raise ValueError(shelving)
        planogram = self.get_agreed_planogram(shelving)
        return not planogram is None
    
    def contains(self, shelving: Shelving):
        return shelving in self.shelving_assignments.keys()
    
    @property
    def shelvings(self):
        return self.shelving_assignments.keys()
    
    @property
    def is_resolved(self):
        for shelving in self.shelving_assignments.keys():
            if not self.is_shelving_resolved(shelving):
                return False
        return True
    
    @property
    def is_declined(self):
        return self._is_declined
    
    @is_declined.setter
    def is_declined(self, value: bool):        
        self._is_declined = value    
    
    def cancel_decline(self):
        self._is_declined = False
    
    def decline(self) -> bool:
        if self.there_is_no_planograms:
            self._is_declined = True            
            return True
        return False