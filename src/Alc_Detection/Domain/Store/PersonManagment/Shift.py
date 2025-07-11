from uuid import UUID
from datetime import datetime, time

from Alc_Detection.Domain.Date.extensions import Period
from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed  
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Schedule import Schedule
from Alc_Detection.Domain.Store.PersonManagment.ShiftAssignment import ShiftAssignment
from Alc_Detection.Domain.Store.PersonManagment.StaffPosition import StaffPosition
from Alc_Detection.Domain.Store.Shelving import Shelving

class Shift(IndexNotifiable):
    def __init__(
        self,
        name: str,
        work_time: tuple[time, time],
        break_time: tuple[time, time],
        staff_positions: list[StaffPosition],
        schedules: list[Schedule]=[],
        on_shift_assignments: list[ShiftAssignment]=[],
        incidents: list[Incident]=[],
        retail_id: str=None,
        id: UUID=None,
    ):
        super().__init__()
        self._retail_id = retail_id             
        self.id = id
        self.name = name 
        self._work_time = work_time
        self._break_time = break_time
        self._schedules = schedules
        self._on_shift_assignments = on_shift_assignments 
        self._incidents = incidents
        
        staff_positions_dict: dict[Post, StaffPosition] = {}
        for s_p in staff_positions:
            staff_positions_dict[s_p.post] = s_p
        self._staff_positions = staff_positions_dict
      
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
    def work_time(self):
        return Period(start=self._work_time[0], end=self._work_time[1])
    
    @property
    def break_time(self):
        return Period(start=self._break_time[0], end=self._break_time[1])
    
    @property
    def incidents(self):
        return self._incidents
    
    @property
    def shift_assignments(self):
        return self._on_shift_assignments
    
    @property    
    def actual_on_shift_assignment(self):
        if len(self._on_shift_assignments) != 0:
            assignments = sorted(self._on_shift_assignments, key=lambda p: p.date, reverse=True)
            return assignments[0]
        return None
    
    @property
    def actual_employees(self):
        if self.actual_on_shift_assignment:
            return [person for person in self.actual_on_shift_assignment.assignments.keys()]
        return []
    
    @property
    def schedules(self):
        return self._schedules
    
    @property
    def schedule(self):
        for schedule in self._schedules:
            now = datetime.now()
            if schedule.between(now):
                return schedule
        return None
    
    @property
    def staff_positions(self):
        return self._staff_positions
    
    def get_incidents_by_period(self, period: Period) -> list[Incident]:
        result = []
        for incident in self._incidents:
            if period.between(incident.send_time):
                result.append(incident)
        return result
    
    def add_incidents(self, *incidents: Incident):
        for incident in incidents:
            self._incidents.insert(0, incident)
    
    def get_unresolved_incidents_by_shelving(self, shelving: Shelving) -> list[Incident]:
        incidents = []
        for incident in self.incidents:
            if incident.shelving == shelving and not incident.is_resolved:
                incidents.append(incident)
        return incidents
    
    def add_schedule(self, new_schedule: Schedule):
        if self._schedules:
            print(self._schedules)            
            for schedule in self._schedules:
                if schedule.is_conflict(new_schedule):
                    raise ValueError(new_schedule)
        self._schedules.append(new_schedule)
    
    def get_post(self, person: Person):
        if not person in self.actual_on_shift_assignment.assignments:
            return None
        return self.actual_on_shift_assignment.assignments[person].post
    
    def get_staff_position_by_post_id(self, post_id: UUID) -> StaffPosition:
        for post, staff_position in self._staff_positions.items():
            if post.id == post_id:
                return staff_position
        return None
    
    def is_employee(self, person: Person):
        return person in self.actual_employees
    
    def new_shift_assignments(
        self,
        assignment_date: datetime,
        persons: list[Person],
        staff_positions: list[StaffPosition]
    ) -> ShiftAssignment: 
        groups: dict[Post, int] = {}
        for staff_position in staff_positions:
            post = staff_position.post
            if not post in self._staff_positions.keys():
                raise ValueError(staff_positions)
            if not post in groups:
                groups[post] = 0
            groups[post] += 1
        for post in groups:
            if groups[post] > self._staff_positions[post].count:
                raise ValueError(staff_positions)
            
        assignments: dict[Person, StaffPosition] = {}
        for person, staff_position in zip(persons, staff_positions):
            assignments[person] = staff_position 
        assignment = ShiftAssignment(
            assignment_date=assignment_date,
            assignments=assignments
        )                     
        self._on_shift_assignments.append(assignment)
        return assignment
    
    def do_work_at(self, date: datetime):
        return not self.schedule.contains(date)
    
    def get_actual_employees_by(self, *posts: Post): 
        employees = []
        for person, staff_position in self.actual_on_shift_assignment.assignments.items():
            if staff_position.post in posts:
                employees.append(person)
        return employees