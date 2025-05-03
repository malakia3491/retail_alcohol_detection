from datetime import datetime
from Alc_Detection.Application.Requests.Models import Person
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.Shelving import Shelving

class Store:
    def __init__(self,
                 name,
                 calibrations:list[Calibration]=[],
                 realograms:list[Realogram]=[],
                 incidents:list[Incident]=[],
                 shifts:list[Shift]=[],
                 id=None):
        self.id = id
        self.name = name 
        self._realograms = sorted(realograms, key=lambda r: r.create_date, reverse=True)
        self._incidents = sorted(incidents, key=lambda i: i.send_time, reverse=True)
        self._shifts = shifts
        self._calibrations = calibrations

    @property
    def calibrations(self) -> list[Calibration]:
        return sorted(self._calibrations, key=lambda calib: calib.create_date, reverse=True)
    
    @property
    def employee(self) -> list[Person]:
        raise NotImplementedError()
    
    @property
    def realograms(self) -> list[Realogram]:
        return self._realograms
    
    @property
    def incidents(self) -> list[Incident]:
        return self._incidents
    
    @property
    def unresolved_incidents(self) -> list[Incident]:
        incidents = []
        for incident in self.incidents:
            if not incident.is_resolved:
                incidents.append(incident)
        return incidents
    
    @property 
    def actual_shift(self):
        for shift in self._shifts:
            if shift.do_work_at(datetime.now()):
                return shift
        return None
    
    def get_actual_planogram_by(self, shelving: Shelving) -> Planogram:
        for calib in self.calibrations:
            if calib.planogram.shelving == shelving:
                return calib.planogram
        return None
    
    def get_planogram_calibration(self, planogram: Planogram) -> Calibration:
        for calib in self.calibrations:
            if calib.planogram == planogram:
                return calib
        return None   
     
    def add_incident(self, *incidents: Incident):
        for incident in incidents:            
            self._incidents.append(incident)
    
    def add_calibration(self, calibration: Calibration):
        self._calibrations.append(calibration)
    
    def add_realogram(self, realogram: Realogram):
        self._realograms.append(realogram)
    
    def add_person(self, person: Person):
        if not self.is_employee(person):
            self._persons.append(person)
            
    def is_employee(self, person: Person) -> bool:
        return person in self.employee
    
    def __eq__(self, other_store):
        return isinstance(other_store, Store) and \
               self.name == other_store.name
               
    def __hash__(self):
        return hash(self.name)