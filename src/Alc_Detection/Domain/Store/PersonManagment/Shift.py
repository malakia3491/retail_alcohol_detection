from uuid import UUID
from datetime import datetime, time

from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Schedule import Schedule
from Alc_Detection.Domain.Store.PersonManagment.ShiftAssignment import ShiftAssignment
from Alc_Detection.Domain.Store.PersonManagment.StaffPosition import StaffPosition

class Shift:
    def __init__(
        self,
        name: str,
        work_time: tuple[time, time],
        break_time: tuple[time, time],
        staff_positions: list[StaffPosition],
        schedules: list[Schedule]=[],
        on_shift_assignments: list[ShiftAssignment]=[],
        incidents: list[Incident]=[],
        id: UUID=None,
    ):
        self.id = id
        self.name = name 
        self.work_time = work_time
        self.break_time = break_time
        self._schedules = schedules
        self._on_shift_assignments = on_shift_assignments 
        self._incidents = incidents
        
        staff_positions_dict: dict[Post, StaffPosition] = {}
        for s_p in staff_positions:
            staff_positions_dict[s_p.post] = s_p
        self._staff_positions = staff_positions_dict
    
    @property
    def incidents(self):
        return self._incidents
    
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
    
    def add_schedule(self, new_schedule: Schedule):
        if self._schedules:            
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