from uuid import UUID
from datetime import datetime, time

from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Schedule import Schedule
from Alc_Detection.Domain.Store.PersonManagment.ShiftAssignment import ShiftAssignment

class Shift:
    def __init__(
        self,
        name: str,
        work_time: tuple[time, time],
        break_time: tuple[time, time],
        staff_positions: dict[Post, int],
        schedules: list[Schedule]=[],
        on_shift_assignments: list[ShiftAssignment]=[],
        id: UUID=None,
    ):
        self.id = id
        self.name = name 
        self.work_time = work_time
        self.break_time = break_time
        self._schedules = schedules
        self._on_shift_assignments = on_shift_assignments 
        self._staff_positions = staff_positions
    
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
    
    def add_schedule(self, schedule: Schedule):
        for schedule in self._schedules:
            if schedule.is_conflict(schedule):
                raise ValueError(schedule)
        self._schedules.append(schedule)
    
    def get_post(self, person: Person):
        if not person in self.actual_on_shift_assignment.assignments:
            return None
        return self.actual_on_shift_assignment.assignments[person]
    
    def is_employee(self, person: Person):
        return person in self.actual_employees
    
    def new_shift_assignments(
        self,
        assignment_date: datetime,
        persons: list[Person],
        posts: list[Post]
    ) -> ShiftAssignment: 
        groups: dict[Post, int] = {}
        for post in posts:
            if not post in self._staff_positions:
                raise ValueError(posts)
            if not post in groups:
                groups[post] = 0
            groups[post] += 1
        for post in groups:
            if groups[post] > self._staff_positions[post]:
                raise ValueError(posts)
            
        assignments: dict[Person, Post] = {}
        for person, post in zip(persons, posts):
            assignments[person] = post 
        assignment = ShiftAssignment(
            assignment_date=assignment_date,
            assignments=assignment
        )                     
        self._on_shift_assignments.append(assignment)
        return assignment
    
    def do_work_at(self, date: datetime):
        return not self._schedule.contains(date)
    
    def get_actual_employees_by(self, *posts: Post):
        person_assignments = self.actual_employees
        employees = []
        for person, post in person_assignments:
            if post in posts:
                employees.append(person)
        return employees