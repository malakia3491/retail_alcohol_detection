from datetime import datetime
from uuid import UUID

from Alc_Detection.Application.Requests.person_management import Person
from Alc_Detection.Domain.Date.extensions import Period
from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.Shelving import Shelving

class Store(IndexNotifiable):
    def __init__(self,
                 login: str,
                 password_hash: str,
                 name,
                 calibrations:list[Calibration]=[],
                 realograms:list[Realogram]=[],
                 shifts:list[Shift]=[],
                 is_office:bool=False,
                 retail_id: str=None,
                 id=None):
        super().__init__()
        self.id = id
        self._retail_id=retail_id
        self._login = login
        self._password_hash = password_hash
        self.name = name 
        self._is_office = is_office
        self._realograms = sorted(realograms, key=lambda r: r.create_date, reverse=True)
        self._shifts = shifts
        self._calibrations = calibrations

    @indexed
    @property
    def login(self) -> str:
        return self._login
    
    @login.setter
    def login(self, value: str):
        old = self._login
        self._login = value
        self._notify_index_changed('login', old, value)
        
    @property
    def password_hash(self) -> str:
        return self._password_hash

    @indexed
    @property
    def retail_id(self) -> bool:
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)

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
    
    def find_realogram_by_id(
        self,
        realogram_id: str
    ) -> Realogram:
        for realogram in self._realograms:
            if realogram.id == realogram_id:
                return realogram
        return None
    
    def get_realograms(
        self,
        period: Period,
        shelving: Shelving=None
    ) -> list[Realogram]:
        realograms = []
        if shelving:
            for realogram in self.realograms:
                if realogram.shelving == shelving and period.between(realogram.create_date):
                    realograms.append(realogram)
        else:
            for realogram in self.realograms:
                if period.between(realogram.create_date):
                    realograms.append(realogram)    
        return realograms
    
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
     
    # def get_using_planograms_by_period(self, period: Period) -> dict[Planogram, tuple[Person, datetime]]:
    #     result: dict[Planogram, tuple[Person, datetime]] = {}
    #     for calibration in self.calibrations:
    #         if period.between(calibration.create_date) and not calibration.planogram in result:
    #             result[calibration.planogram] = (calibration.creator, calibration.create_date)
    #     return result
    
    def _get_planogram_calibrations_dict(self) -> dict[Planogram, list[Calibration]]:
        result: dict[Planogram, list[Calibration]] = {}
        for calibration in self.calibrations:
            if not calibration.planogram in result:
                 result[calibration.planogram] = []
            result[calibration.planogram].append(calibration)
        return result
    
    def get_using_planograms_by_period(self, period: Period) -> dict[Planogram, tuple[tuple[Person, datetime], Period]]:
        calibrations_by_planogram = self._get_planogram_calibrations_dict() 
        
        print("КОЛИЧЕСТВО ПЛАНОГРАММ", len(calibrations_by_planogram.keys()))
        
        sorted_planograms = sorted(
            calibrations_by_planogram.keys(),
            key=lambda pg: min(c.create_date for c in calibrations_by_planogram[pg])
        )
        result = {}
        
        for i in range(len(sorted_planograms)):
            current_pg = sorted_planograms[i]
            current_calibrations = sorted(
                calibrations_by_planogram[current_pg], 
                key=lambda x: x.create_date
            )
            
            last_calibration = current_calibrations[-1]
            person = last_calibration.creator
            start_date = last_calibration.create_date
            if period.between(start_date):
                if i < len(sorted_planograms) - 1:
                    next_pg = sorted_planograms[i + 1]
                    next_calibrations = sorted(
                        calibrations_by_planogram[next_pg], 
                        key=lambda x: x.create_date
                    )
                    end_date = next_calibrations[0].create_date
                else:
                    end_date = period.end        
                pg_period = Period(start_date, end_date)  
                result[current_pg] = (
                    (person, start_date), 
                    pg_period
                )
        return result
    
    def get_realograms_by_shelving_period(self, shelving: Shelving, period: Period):
        realograms = self.get_realograms_by_shelving(shelving)
        result: list[Realogram] = []
        for realogram in realograms:
            if period.between(realogram.create_date):
                result.append(realogram)
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