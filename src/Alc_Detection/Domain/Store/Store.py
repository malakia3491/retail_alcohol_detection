from datetime import datetime
from uuid import UUID
from Alc_Detection.Application.Requests.Models import Person
from Alc_Detection.Domain.Date.extensions import Period
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.Shelving import Shelving

class Store:
    def __init__(self,
                 name,
                 calibrations:list[Calibration]=[],
                 realograms:list[Realogram]=[],
                 shifts:list[Shift]=[],
                 is_office:bool=False,
                 id=None):
        self.id = id
        self.name = name 
        self._is_office = is_office
        self._realograms = sorted(realograms, key=lambda r: r.create_date, reverse=True)
        self._shifts = shifts
        self._calibrations = calibrations

    @property
    def is_office(self) -> bool:
        return self._is_office

    @property
    def calibrations(self) -> list[Calibration]:
        return sorted(self._calibrations, key=lambda calib: calib.create_date, reverse=True)
    
    @property
    def employee(self) -> list[Person]:
        employees = []
        for shift in self._shifts:
            employees.extend(shift.actual_employees)
        return employees
    
    @property
    def realograms(self) -> list[Realogram]:
        return self._realograms
    
    @property
    def shifts(self) -> list[Shift]:
        return self._shifts
    
    @property 
    def actual_shift(self):
        for shift in self._shifts:
            if shift.do_work_at(datetime.now()):
                return shift
        return None
    
    def find_shift_by_id(
        self,
        shift_id: str
    ) -> Shift:
        for shift in self._shifts:
            if shift.id == shift_id:
                return shift
        return None 
    
    def get_actual_realograms(
        self,
        shelvings: list[Shelving]
    ) -> dict[Shelving, Realogram]:
        actual_realograms: dict[Shelving, Realogram] = {}
        for shelving in shelvings:
            for realogram in self.realograms:
                if realogram.shelving == shelving:
                    actual_realograms[shelving] = realogram
                    break
        return actual_realograms
    
    def find_shift_by_id(self, id: UUID) -> Shift:
        for shift in self._shifts:
            if shift.id == id:
                return shift
        return None
    
    def get_work_place(self, person: Person) -> tuple[Shift, Post]:
        for shift in self._shifts:
            if shift.is_employee(person):
                post = shift.get_post(person)
                return (shift, post)
        return None
    
    def is_employee(self, person: Person):
        for shift in self._shifts:
            if shift.is_employee(person):
                return True
        return False
    
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
     
    def get_using_planograms_by_period(self, period: Period) -> dict[Planogram, tuple[Person, datetime]]:
        result: dict[Planogram, tuple[Person, datetime]] = {}
        for calibration in self.calibrations:
            if period.between(calibration.create_date) and not calibration.planogram in result:
                result[calibration.planogram] = (calibration.creator, calibration.create_date)
        return result
    
    def get_realograms_by_shelving(self, shelving: Shelving) -> list[Realogram]:
        result: list[Realogram] = []
        for realogram in self.realograms:
            if realogram.shelving == shelving:
                result.append(realogram)
        return result
    
    def add_shifts(self, *shifts: Shift):
        for shift in shifts:
            self._shifts.append(shift)
    
    def add_calibration(self, calibration: Calibration):
        self._calibrations.insert(0, calibration)
    
    def add_realogram(self, realogram: Realogram):
        self._realograms.insert(0, realogram)
    
    def add_person(self, shift: Shift, persons: list[Person], posts: list[Post]):
        if len(persons) != len(posts):
            raise ValueError((persons, posts))
        if not shift in self._shifts:
            raise ValueError(shift)
        shift.new_shift_assignments(
            assignment_date=datetime.now(),
            persons=persons,
            posts=posts
        )
            
    def is_employee(self, person: Person) -> bool:
        return person in self.employee
    
    def __eq__(self, other_store):
        return isinstance(other_store, Store) and \
               self.name == other_store.name
               
    def __hash__(self):
        return hash(self.name)