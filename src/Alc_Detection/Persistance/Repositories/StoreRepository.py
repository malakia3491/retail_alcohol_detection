from uuid import UUID
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from typing import Union, List, Optional

from Alc_Detection.Domain.Entities import Store
from Alc_Detection.Application.Mappers.Mappers import StoreMapper
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Persistance.Cache.CacheBase import CacheBase
from Alc_Detection.Persistance.Models.Models import Calibration as CalibrationModel
from Alc_Detection.Persistance.Models.Models import CalibrationBox as CalibrationBoxModel
from Alc_Detection.Persistance.Models.Models import Store as StoreModel
from Alc_Detection.Persistance.Models.Models import RealogramSnapshot as RealogramModel
from Alc_Detection.Persistance.Models.Models import RealogramDetection as RealogramDetectionModel
from Alc_Detection.Persistance.Models.Models import Incident as IncidentModel

class StoreRepository:
    def __init__(self,
                 session_factory: AsyncSession,
                 cache: CacheBase,
                 store_mapper: StoreMapper): 
        self.session_factory = session_factory
        self._store_mapper = store_mapper
        self._cache = cache

    async def on_start(self):
        async with self.session_factory() as session:
            result = await session.execute(select(StoreModel))
            [self._cache.put(row.id, self._store_mapper.map_to_domain_model(row)) for row in result.scalars().all()]
            
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
                        matrix_cords=box.position,
                        box_cords=[box.p_min.x, box.p_min.y, box.p_max.x, box.p_max.y],
                        is_empty=box.is_empty,
                        is_incorrect_pos=box.is_incorrect_position
                    ))            
            
            realogram_db = RealogramModel(
                store_id=store.id,
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
        *incident: Incident
    ) -> int:
        if self._cache.contains(store):
            incident_db = IncidentModel()
            
            async with self.session_factory() as session:
                session.add(incident_db)
                await session.commit()
                await session.refresh(incident_db)  
            incident.id = incident_db.id                    
            return len([incident_db])
        return 0        
    
    async def update_incidents(
        self,
        store: Store,
        *incidents: Incident 
    ) -> int:
        raise NotImplementedError()