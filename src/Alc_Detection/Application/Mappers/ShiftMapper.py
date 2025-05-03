
from datetime import datetime
from uuid import UUID
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Application.Mappers.ScheduleMapper import ScheduleMapper
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.PersonManagment.ShiftAssignment import ShiftAssignment
from Alc_Detection.Persistance.Models.Models import StoreShift as StoreShiftModel

class ShiftMapper:
    def __init__(
        self,
        person_mapper: PersonMapper,
        schedule_mapper: ScheduleMapper
    ):
        self._person_mapper = person_mapper
        self._schedule_mapper = schedule_mapper        
    
    def map_to_domain_model(self, db_model: StoreShiftModel) -> Shift:
        if db_model is None: return None
        if not isinstance(db_model, StoreShiftModel):
            raise ValueError(db_model)           
        on_shift_assignments: dict[UUID, dict[Person, Post]] = {}
        dates: list[datetime] = []
        for staff_position in db_model.shift_posts:
            post = Post(id=staff_position.post.id, name=staff_position.post.name)            
            for person_assignment in staff_position.shift_post_persons:
                if not person_assignment.shift_assignment_id in on_shift_assignments:
                    on_shift_assignments[person_assignment.shift_assignment_id] = {}
                    dates.append(person_assignment.shift_assignment.assignment_date)
                person = self._person_mapper.map_to_domain_model(person_assignment.person)
                on_shift_assignments[person_assignment.shift_assignment_id][person] = post 
                
        shift_assignments = [ShiftAssignment(assignment_date=date,
                                             asignments=on_shift_assignments[id])
                             for id, date in zip(on_shift_assignments, dates)]                              
        return Shift(
            id=db_model.id,
            name=db_model.name,
            work_time=(db_model.time_work_start, db_model.time_work_end),
            break_time=(db_model.time_break_start, db_model.time_break_end),
            schedule=self._schedule_mapper.map_to_domain_model(db_model.schedule),
            on_shift_assignments=shift_assignments)