from datetime import datetime, time
from uuid import UUID

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
        schedule: Schedule,
        on_shift_assignments: list[ShiftAssignment],
        id: UUID=None,
    ):
        self.id = id
        self.name = name 
        self.work_time = work_time
        self.break_time = break_time
        self._schedule = schedule
        self._on_shift_assignments = on_shift_assignments 
    
    @property    
    def actual_on_shift_assignment(self):
        if len(self._on_shift_assignments) != 0:
            assignments = sorted(self._on_shift_assignments, key=lambda p: p.date, reverse=True)
            return assignments[0]
        return None
    
    @property
    def actual_employees(self):
        return self.actual_on_shift_assignment.assignments
    
    def do_work_at(self, date: datetime):
        return not self._schedule.contains(date)
    
    def get_actual_employees_by(self, *posts: Post):
        person_assignments = self.actual_employees
        employees = []
        for person, post in person_assignments:
            if post in posts:
                employees.append(person)
        return employees