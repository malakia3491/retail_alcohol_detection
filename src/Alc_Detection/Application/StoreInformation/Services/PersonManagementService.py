from datetime import datetime
import traceback
from fastapi import HTTPException, status

from Alc_Detection.Application.Mappers.ScheduleMapper import ScheduleMapper
from Alc_Detection.Application.Mappers.ShiftMapper import ShiftMapper
from Alc_Detection.Domain.Entities import *
from Alc_Detection.Application.StoreInformation.Exceptions.Exceptions import (
     PersonIsNotWorkerAlready
)
from Alc_Detection.Application.Requests.Requests import (
    AddPermitionsRequest, AddPersonsRequest, AddPostsRequest, AddScheduleRequest, AddShiftAssignment, AddShiftsRequest, DismissPersonRequest,
)
from Alc_Detection.Domain.Store.PersonManagment.Permition import Permition
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.PersonManagment.StaffPosition import StaffPosition
from Alc_Detection.Persistance.Repositories.PermitionRepository import PermitionRepository
from Alc_Detection.Persistance.Repositories.PostRepository import PostRepository
from Alc_Detection.Persistance.Repositories.Repositories import *

class PersonManagementService:
    def __init__(self,
                 store_repository: StoreRepository,
                 person_repository: PersonRepository,
                 post_repository: PostRepository,
                 shift_mapper: ShiftMapper,
                 schedule_mapper: ScheduleMapper,
                 permition_repository: PermitionRepository
    ):
        self._shift_mapper = shift_mapper
        self._post_repository = post_repository
        self._store_repository = store_repository
        self._person_repository = person_repository
        self._schedule_mapper = schedule_mapper
        self._permition_repository = permition_repository

    async def add_shift_assignment(
        self,
        request: AddShiftAssignment
    ) -> str:
        try:
            store = await self._store_repository.get(request.store_id)
            shift = store.find_shift_by_id(request.shift_id)
            if shift:
                staff_positions: list[StaffPosition] = []
                persons: list[Person] = []
                for assignment in request.assignments:
                    person = await self._person_repository.get(assignment.person_id)                
                    staff_positions.append(shift.get_staff_position_by_post_id(assignment.post_id))
                    persons.append(person)
                    
                shift_assignment = shift.new_shift_assignments(
                    assignment_date=datetime.now(),
                    persons=persons,
                    staff_positions=staff_positions,
                )
                count_added_records = await self._store_repository.add_shift_assignment(
                    store,
                    shift_assignment
                )
                return f"Succsessfully. {count_added_records} was added."
            else: 
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=ex.__str__())    
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())    
    
    async def get_work_place(
        self,
        person: Person
    ) -> tuple[Store, Shift, Post]:
        try:
            stores = await self._store_repository.get_all()
            for store in stores:
                if store.is_employee(person):
                    shift, post = store.get_work_place(person)
                    return store, shift, post 
            return None, None, None
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())
    
    async def add_permitions(self, request: AddPermitionsRequest) -> str:
        try:
            permitions: list[Permition] = []
            for req_permition in request.permitions:
                permition = Permition(name=req_permition.name)
                permitions.append(permition)
            count_added_records = await self._permition_repository.add(*permitions)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())             
    
    async def add_posts(self, request: AddPostsRequest) -> str:
        try:
            posts = []
            for req_post in request.posts:
                permitions: list[Permition] = []
                for req_permition in req_post.permitions:
                    permition = await self._permition_repository.get(req_permition)
                    permitions.append(permition)
                post = Post(
                    name=req_post.name,
                    permitions=permitions
                )
                posts.append(post)
            count_added_records = await self._post_repository.add(*posts)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     
       
    async def add_persons(self, request: AddPersonsRequest) -> str:
        try:
            persons = []
            for request_person in request.persons:
                person = Person(name=request_person.name,
                                    telegram_id=request_person.telegram_id)
                persons.append(person)
            count_added_records = await self._person_repository.add(*persons)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     
        
    async def dismiss_employee(self, request: DismissPersonRequest) -> str:
        field = "is_store_worker"             
        person_data = {field: False}        
        try:
            person = await self._person_repository.get(request.person_id)
            if not person.is_store_worker:
                raise PersonIsNotWorkerAlready(person.name)
                            
            record_count = await self._person_repository.update(request.person_id, person_data)
            return f"Succsessfully. Updated {record_count} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())               

    async def set_schedule(
        self,
        request: AddScheduleRequest
    ) -> str:
        try:
            store = await self._store_repository.get(request.store_id)
            shift = store.find_shift_by_id(request.shift_id)
            if shift:
                schedule = self._schedule_mapper.map_request_to_domain_model(request.schedule)
                count_added_records = await self._store_repository.add_schedules(
                    store,
                    shift,
                    schedule
                )
                shift.add_schedule(schedule)
                return f"Successfully. Added {count_added_records} records."
            return "Unsuccessfully. Shift is not found"
        except ValueError as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ex.__str__())     
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())    
            
    async def add_shifts(self, request: AddShiftsRequest) -> str:
        try:
            store = await self._store_repository.get(request.store_id)
            shifts = []
            for req_shift in request.shifts:
                staff_positions: list[StaffPosition] = {}
                for staff_position in req_shift.staff_positions:
                    post = await self._post_repository.get(staff_position)
                    staff_positions = StaffPosition(post=post, count=req_shift.staff_positions[staff_position])
                req_shift.staff_positions = staff_positions
                shifts.append(self._shift_mapper.map_request_to_domain_model(req_shift))
            store.add_shifts(*shifts)
            count_added_records = await self._store_repository.add_shifts(store, *shifts)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())    