from datetime import time
from uuid import UUID
from Alc_Detection.Domain.Store.Person import Person

class Shift:
    def __init__(
        self,
        name: str,
        work_time: tuple[time, time],
        break_time: tuple[time, time],
        schedule,
        id: UUID=None,
        persons=[]
    ):
        self.id = id
        self.name = name 
        self.work_time = work_time
        self.break_time = break_time
        self.schedule = schedule
        self.employees = persons 
        
    def get_administrators() -> list[Person]:
        raise NotImplemented()
    
    def get_workers() -> list[Person]:
        raise NotImplemented()