from datetime import datetime
from uuid import UUID
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Application.Mappers.ScheduleMapper import ScheduleMapper
from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.PersonManagment.ShiftAssignment import ShiftAssignment
from Alc_Detection.Persistance.Models.Models import StoreShift as StoreShiftModel
from Alc_Detection.Application.Requests.Models import Shift as ShiftApiModel
from Alc_Detection.Persistance.Models.Models import ShiftPost as ShiftPostModel

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
        staff_positions: dict[Post, int] = {}
        for staff_position in db_model.shift_posts:
            post = Post(id=staff_position.post.id, name=staff_position.post.name)
            staff_positions[post] = staff_position.count          
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
            schedules=[self._schedule_mapper.map_to_domain_model(schedule_db) for schedule_db in db_model.schedules],
            staff_positions=staff_positions,
            on_shift_assignments=shift_assignments)
        
    def map_request_to_domain_model(self, req_model: ShiftApiModel)-> Shift:
        if req_model is None: return None
        if not isinstance(req_model, ShiftApiModel):
            raise ValueError(req_model)    
        return Shift(
            name=req_model.name,
            work_time=(req_model.work_time_start, req_model.work_time_end),
            break_time=(req_model.break_time_start, req_model.break_time_end),
            staff_positions=req_model.staff_positions,
            schedules=[self._schedule_mapper.map_request_to_domain_model(req_model.schedule)]                    
        )
    
    def map_to_db_model(self, store: Store, domain_model: Shift) -> StoreShiftModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Shift):
            raise ValueError(domain_model)        
        
        shift_posts: list[ShiftPostModel] = []
        for post, count in domain_model.staff_positions.items():
            shift_post = ShiftPostModel(
                post_id=post.id,
                count=count)
            shift_posts.append(shift_post)
        db_schedules = [] 
        for schedule in domain_model.schedules:
            if schedule: db_schedules.append(self._schedule_mapper.map_to_db_model(shift=domain_model, domain_model=schedule))
        return StoreShiftModel(
            store_id=store.id,
            name=domain_model.name,
            time_work_start=domain_model.work_time[0],
            time_work_end=domain_model.work_time[1],
            time_break_start=domain_model.break_time[0],
            time_break_end=domain_model.break_time[1],
            shift_posts=shift_posts,
            schedules=db_schedules,            
        )          