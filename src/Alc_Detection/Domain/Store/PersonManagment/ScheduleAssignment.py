from Alc_Detection.Domain.Store.PersonManagment.Schedule import Schedule
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift

class ScheduleAssignment:
    def __init__(
        self,
        schedule: Schedule,
        shift: Shift,
        id:str=None
    ):
        self.id = id
        self._schedule = schedule
        self._shift = shift
        
    @property
    def schedule(self):
        return self._schedule
    
    @property
    def shift(self):
        return self._shift    
        