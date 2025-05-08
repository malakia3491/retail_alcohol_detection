from datetime import datetime
from uuid import UUID
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Application.Mappers.ScheduleMapper import ScheduleMapper
from Alc_Detection.Application.Mappers.ShiftMapper import ShiftMapper
from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from sqlalchemy import case, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from typing import Union, List, Optional

from Alc_Detection.Domain.Entities import Store
from Alc_Detection.Application.Mappers.Mappers import StoreMapper
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Store.PersonManagment.Schedule import Schedule
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.PersonManagment.ShiftAssignment import ShiftAssignment
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase
from Alc_Detection.Persistance.Exceptions import ObjectUpdateException
from Alc_Detection.Persistance.Models.Models import Calibration as CalibrationModel
from Alc_Detection.Persistance.Models.Models import CalibrationBox as CalibrationBoxModel
from Alc_Detection.Persistance.Models.Models import Store as StoreModel
from Alc_Detection.Persistance.Models.Models import RealogramSnapshot as RealogramModel
from Alc_Detection.Persistance.Models.Models import RealogramDetection as RealogramDetectionModel
from Alc_Detection.Persistance.Models.Models import Incident as IncidentModel
from Alc_Detection.Persistance.Models.Models import StoreShift as ShiftModel
from Alc_Detection.Persistance.Models.Models import ShiftAssignment as ShiftAssignmentModel
from Alc_Detection.Persistance.Models.ShelfDetection.RealogramDetection import RealogramDetection
from Alc_Detection.Persistance.Models.StoreModels.ShiftPostPerson import ShiftPostPerson
from Alc_Detection.Persistance.Models.StoreModels.Person import Person as PersonModel

class StoreRepository:
    def __init__(self,
                 session_factory: AsyncSession,
                 cache: CacheBase,
                 store_mapper: StoreMapper,
                 shift_mapper: ShiftMapper,
                 schedule_mapper: ScheduleMapper,
                 person_mapper: PersonMapper): 
        self.session_factory = session_factory
        self._store_mapper = store_mapper
        self._shift_mapper = shift_mapper
        self._person_mapper = person_mapper
        self._schedule_mapper = schedule_mapper
        self._cache = cache

    async def on_start(self):
        async with self.session_factory() as session:
            result = await session.execute(select(StoreModel))
            [self._cache.put(row.id, self._store_mapper.map_to_domain_model(row)) for row in result.scalars().all()]         
         
    async def get_all(self) -> list[Store]:
        return self._cache.get_all()
    
    async def get_all_not_office(self) -> list[Store]:
        stores = self._cache.get_all()
        result = []
        for store in stores:
            if not store.is_office:
                result.append(store)
        return result
    
    async def get(self, *ids: UUID) -> Store | List[Store]:
        in_cache_ids, not_in_cache_ids = self._cache.in_cache(*ids)
        objs = [self._cache.get(id) for id in in_cache_ids]
        if len(not_in_cache_ids) == 0:
            if len(objs) == 1: return objs[0]
            else: return objs
        else: 
            async with self.session_factory() as session:
                try:
                    stm_result = await session.execute(select(StoreModel).where(StoreModel.id.in_(not_in_cache_ids)))
                    db_objs = [self._store_mapper.map_to_domain_model(model) for model in stm_result.scalars().all()]
                    for db_obj in db_objs:
                        self._cache.put(db_obj.id, db_obj)
                        objs.append(db_obj)
                except NoResultFound as ex:
                    raise ValueError(f"Записи с айди {not_in_cache_ids} не найдены")
        if len(objs) == 1: return objs[0]
        else: return objs
    
    async def add_shift_assignment(
        self,
        store: Store,
        *new_objs: ShiftAssignment
    ) -> int:
        if self._cache.contains(store):
            shift_assignments_db = []
            for shift_assignment in new_objs:
                shift_post_persons = []
                for person, staff_position in shift_assignment.assignments.items():
                    shift_post_persons.append(ShiftPostPerson(
                        shift_post_id = staff_position.id,
                        person_id = person.id
                    ))
                shift_assignment_db = ShiftAssignmentModel(
                    assignment_date=shift_assignment.date,
                    shift_post_persons=shift_post_persons        
                )
                shift_assignments_db.append(shift_assignment_db)
                            
            async with self.session_factory() as session:
                session.add_all(shift_assignments_db)
                await session.commit()
                [await session.refresh(shift_assignment_db) for shift_assignment_db in shift_assignments_db]
                for shift_assignment_db, shift_assignmnet in zip(shift_assignments_db, new_objs):
                    shift_assignmnet.id = shift_assignment_db.id                
            return len([shift_assignments_db])
        return 0 
    
    async def add(self, *new_objs: Store) -> int:
        objs = []
        for new_obj in new_objs:                
            if self._cache.contains(new_obj): continue
            objs.append(self._store_mapper.map_to_db_model(new_obj))
            
        if len(objs) == 0: return 0
        async with self.session_factory() as session:
            session.add_all(objs)
            await session.commit()
            for obj in objs: await session.refresh(obj)  
        for obj in objs:
            self._cache.put(obj.id, self._store_mapper.map_to_domain_model(obj))
        return len(objs)
    
    async def add_calibration(self,
                              store: Store,
                              calibration: Calibration
    ) -> int:
        if self._cache.contains(store):
            store.add_calibration(calibration)
            
            calibration_boxes = [CalibrationBoxModel(box_cords=box.xyxy,
                                                     matrix_cords=box.matrix_cords.to_list(),
                                                     conf=box.conf) 
                                 for box in calibration.calibrations_boxes]            
            calibration_db = CalibrationModel(
                store_id=store.id,
                person_id=calibration.creator.id,
                planogram_id=calibration.planogram.id,
                calibration_date=calibration.create_date,
                calibration_boxes=calibration_boxes
            )
            
            async with self.session_factory() as session:
                session.add(calibration_db)
                await session.commit()
                await session.refresh(calibration_db)  
            calibration.id = calibration_db.id                    
            return len([calibration_db])
        return 0
    
    async def add_realogram(self,
                            store: Store,
                            realogram: Realogram
    ) -> int:
        if self._cache.contains(store):
            detections = []
            for _, shelf in realogram.product_matrix:
                for box in shelf.boxes:
                    detections.append(RealogramDetectionModel(
                        product_id=box.product.id,
                        matrix_cords=box.position.to_list(),
                        box_cords=box.cords,
                        conf=box.conf,
                        is_empty=box.is_empty,
                        is_incorrect_pos=box.is_incorrect_position
                    ))            
            
            realogram_db = RealogramModel(
                store_id=store.id,
                planogram_id=realogram.planogram.id,
                shelving_id=realogram.shelving.id,
                datetime_upload=realogram.create_date,
                img_src=realogram.image_source,
                empty_count=realogram.empty_count,
                planogram_accordance=realogram.accordance,
                detections=detections
            )
            
            async with self.session_factory() as session:
                session.add(realogram_db)
                await session.commit()
                await session.refresh(realogram_db)  
            realogram.id = realogram_db.id                    
            return len([realogram_db])
        return 0
    
    async def add_incident(
        self,
        store: Store,
        shift: Shift,
        *incidents: Incident
    ) -> int:
        if self._cache.contains(store):
            incidents_db = []
            for incident in incidents:
                persons = []
                for person in incident.responsible_employees:
                    person = self._person_mapper.map_to_db_model(person)
                    persons.append(person)
                detections = []
                for deviation in incident.deviations:
                    r_product_id = deviation.right_product.id if deviation.product_box.is_incorrect_position else None
                    detection = RealogramDetectionModel(
                        id=deviation.product_box.id,
                        realogram_id=incident.realogram.id,
                        product_id=deviation.product.id,
                        right_product_id=r_product_id,
                        matrix_cords=deviation.position.to_list(),
                        box_cords=deviation.product_box.cords,
                        conf=deviation.product_box.conf,
                        is_empty=deviation.product_box.is_empty,
                        is_incorrect_pos=deviation.product_box.is_incorrect_position,
                    )
                    detections.append(detection)
                incident_db = IncidentModel(
                    store_shift_id=shift.id,
                    send_time=incident.send_time,
                    message=incident.build_message_text(),
                    persons=persons,
                    type=incident.type,
                    detections=detections                
                )
                incidents_db.append(incident_db)
            
            async with self.session_factory() as session:
                session.add_all(incidents_db)
                await session.commit()
                for incident in incidents_db: await session.refresh(incident)  
            for incident_db, incident in zip(incidents_db, incidents):
                incident.id = incident_db.id                 
            return len([incidents_db])
        return 0        
    
    async def add_shifts(
        self,
        store: Store,
        *shifts: Shift
    ) -> int:
        if self._cache.contains(store):
            shifts_db = []
            for shift in shifts:
                shift_db = self._shift_mapper.map_to_db_model(store=store, domain_model=shift)
                shifts_db.append(shift_db)         
            async with self.session_factory() as session:
                session.add_all(shifts_db)
                await session.commit()
                for incident in shifts_db: await session.refresh(incident)  
            for shift_db, shift in zip(shifts_db, shifts):
                shift.id = shift_db.id                 
            return len([shifts_db])
        return 0     
    
    async def add_schedules(
        self,
        store: Store,
        shift: Shift,
        *schedules: Schedule 
    ) -> int:
        if self._cache.contains(store):
            schedules_db = []
            for schedule in schedules:
                schedule_db = self._schedule_mapper.map_to_db_model(shift=shift, domain_model=schedule)
                schedules_db.append(schedule_db)         
            async with self.session_factory() as session:
                session.add_all(schedules_db)
                await session.commit()
                for schedule_db in schedules_db: await session.refresh(schedule_db)  
            for schedule_db, schedule in zip(schedules_db, schedules):
                schedule.id = schedule_db.id                 
            return len(schedules_db)
        return 0   
    
    async def update_incidents(
        self,
        store: Store,
        elimination_time: datetime,
        *incidents: Incident 
    ) -> int:
        if self._cache.contains(store):
            incident_ids = []
            for incident in incidents:
                if incident.is_resolved: incident_ids.append(incident.id)
            target_ids = [incident.id for incident in incidents]
            try:                
                async with self.session_factory() as session:
                    stmt = (
                        update(IncidentModel)
                        .where(IncidentModel.id.in_(incident_ids))
                        .values(elimination_time=elimination_time)
                    )
                    stmt = (
                        update(RealogramDetectionModel)
                        .where(RealogramDetectionModel.incident_id.in_(target_ids))
                        .values(elimination_time=elimination_time)
                    )
                    await session.execute(stmt)
                    await session.commit()
            except Exception as ex:
                raise ex
        else:
            raise ObjectUpdateException(object_type=Store, object_id=store.id)
        return len([store])
    
    async def update_incidents_elimination_time(
        self,
        store: Store,
        *incidents: Incident
    ) -> int:
        """
        Bulk‑update elimination_time для инцидентов одним запросом через CASE WHEN.
        """
        if not self._cache.contains(store):
            raise ObjectUpdateException(Store, store.id)
        
        mapping = {
            inc.id: inc.elimination_time
            for inc in incidents
            if inc.elimination_time is not None
        }
        if not mapping:
            return 0
        
        case_stmt = case(mapping, value=IncidentModel.id)

        try:
            async with self.session_factory() as session:
                stmt = (
                    update(IncidentModel)
                    .where(IncidentModel.id.in_(mapping.keys()))
                    .values(elimination_time=case_stmt)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount
        except Exception as ex:
            raise ObjectUpdateException(
                Incident,
                list(mapping.keys()),
                ex
            )
        
    async def update_detections_elimination_time(
            self,
            store: Store,
            elimination_time: datetime,
            *deviations: Deviation
        ) -> int:
            """
            Обновляет поле elimination_time у переданных отклонений.
            """
            if not self._cache.contains(store):
                raise ObjectUpdateException(Store, store.id)

            ids = [d.id for d in deviations]
            if not ids:
                return 0

            try:
                async with self.session_factory() as session:
                    stmt = (
                        update(RealogramDetectionModel)
                        .where(RealogramDetectionModel.id.in_(ids))
                        .values(elimination_time=elimination_time)
                    )
                    res = await session.execute(stmt)
                    await session.commit()
                    return res.rowcount
            except Exception as ex:
                raise ObjectUpdateException(RealogramDetection, ids, ex)