from datetime import datetime
from uuid import UUID
from Alc_Detection.Application.Mappers.IncidentMapper import IncidentMapper
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Application.Mappers.ScheduleMapper import ScheduleMapper
from Alc_Detection.Domain.Store.PersonManagment.Permition import Permition
from Alc_Detection.Domain.Store.PersonManagment.StaffPosition import StaffPosition
from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.PersonManagment.ShiftAssignment import ShiftAssignment
from Alc_Detection.Persistance.Models.Models import StoreShift as StoreShiftModel
from Alc_Detection.Persistance.Models.Models import Post as PostModel
from Alc_Detection.Application.Requests.person_management import Shift as ShiftApiModel
from Alc_Detection.Persistance.Models.Models import ShiftPost as ShiftPostModel
from Alc_Detection.Persistance.Models.Models import ShiftPostPerson as ShiftPostPersonModel
from Alc_Detection.Persistance.Models.Models import ShiftAssignment as ShiftAssignmentModel

class ShiftMapper:
    def __init__(
        self,
        person_mapper: PersonMapper,
        schedule_mapper: ScheduleMapper,
        incident_mapper: IncidentMapper
    ):
        self._person_mapper = person_mapper
        self._schedule_mapper = schedule_mapper
        self._incident_mapper = incident_mapper        
    
    def map_to_domain_model(self, db_model: StoreShiftModel) -> Shift:
        if db_model is None: return None
        if not isinstance(db_model, StoreShiftModel):
            raise ValueError(db_model)
        incidents = []
        for incident_db in db_model.incidents:
            incident = self._incident_mapper.map_db_to_domain(incident_db)
            incidents.append(incident)     
                   
        on_shift_assignments: dict[UUID, dict[Person, StaffPosition]] = {}
        dates: list[datetime] = []
        staff_positions: list[StaffPosition] = []
        for staff_position_db in db_model.shift_posts:
            permitions = [Permition(name=post_per.permition.name, id=post_per.permition.id) for post_per in staff_position_db.post.post_permitions]
            post = Post(id=staff_position_db.post.id, name=staff_position_db.post.name, permitions=permitions)
            staff_position = StaffPosition(post=post, count=staff_position_db.count, id=staff_position_db.id)
            staff_positions.append(staff_position)         
            for person_assignment in staff_position_db.shift_post_persons:
                if not person_assignment.shift_assignment_id in on_shift_assignments:
                    on_shift_assignments[person_assignment.shift_assignment_id] = {}
                    dates.append(person_assignment.shift_assignment.assignment_date)
                person = self._person_mapper.map_to_domain_model(person_assignment.person)
                on_shift_assignments[person_assignment.shift_assignment_id][person] = staff_position 
                
        shift_assignments = [ShiftAssignment(assignment_date=date,
                                             assignments=on_shift_assignments[id])
                             for id, date in zip(on_shift_assignments, dates)]                              
        return Shift(
            id=db_model.id,
            retail_id=db_model.retail_id,
            name=db_model.name,
            work_time=(db_model.time_work_start, db_model.time_work_end),
            break_time=(db_model.time_break_start, db_model.time_break_end),
            schedules=[self._schedule_mapper.map_to_domain_model(schedule_db) for schedule_db in db_model.schedules],
            staff_positions=staff_positions,
            on_shift_assignments=shift_assignments,
            incidents=incidents)
        
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
        for post, staff_position in domain_model.staff_positions.items():
            shift_post = ShiftPostModel(post_id=post.id,
                                        retail_id=staff_position.retail_id,
                                        count=staff_position.count)
            shift_posts.append(shift_post)
            
        position_to_shift_post_person: dict[str, list] = {}
        for shift_assignment in domain_model.shift_assignments:
            db_shift_assignment = ShiftAssignmentModel(
                assignment_date=shift_assignment.date,
                retail_id=shift_assignment.retail_id,                
            )
            for person, staff_position in shift_assignment.assignments.items():
                curr_db_staff_position = None
                for db_shift_post in shift_posts:
                    if db_shift_post.post_id == staff_position.post.id:
                        curr_db_staff_position = db_shift_post
                        position_to_shift_post_person[staff_position.post.id] = [] 
                        break
                position_to_shift_post_person[staff_position.post.id].append(
                    ShiftPostPersonModel(
                        person_id=person.id,
                        shift_post=curr_db_staff_position,
                        shift_assignment=db_shift_assignment,
                    )
                )
        for post_id, shift_post_persons in position_to_shift_post_person.items():
            for shift_post in shift_posts:
                if shift_post.post_id == post_id:
                    shift_post.shift_post_persons = shift_post_persons

        db_schedules = [] 
        for schedule in domain_model.schedules:
            if schedule: db_schedules.append(self._schedule_mapper.map_to_db_model(shift=domain_model, domain_model=schedule))
        return StoreShiftModel(
            retail_id=domain_model.retail_id,
            store_id=store.id,
            name=domain_model.name,
            time_work_start=domain_model.work_time.start,
            time_work_end=domain_model.work_time.end,
            time_break_start=domain_model.break_time.start,
            time_break_end=domain_model.break_time.end,
            shift_posts=shift_posts,
            schedules=db_schedules,          
        )          