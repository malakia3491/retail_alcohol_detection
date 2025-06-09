from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Application.Mappers.CalibrationMapper import CalibrationMapper
from Alc_Detection.Application.Mappers.RealogramMapper import RealogramMapper
from Alc_Detection.Application.Mappers.ShiftMapper import ShiftMapper
from Alc_Detection.Application.Requests.retail import Store as StoreApiModel
from Alc_Detection.Persistance.Models.Models import Store as StoreModel 

class StoreMapper:    
    def __init__(self,
                 calibration_mapper: CalibrationMapper,
                 realogram_mapper: RealogramMapper,
                 shift_mapper: ShiftMapper,             
    ):
        self._calibration_mapper = calibration_mapper
        self._realogram_mapper = realogram_mapper
        self._shift_mapper = shift_mapper
    
    def map_to_domain_model(self, db_model: StoreModel) -> Store:
        if db_model is None: return None
        if not isinstance(db_model, StoreModel):
            raise ValueError(db_model)
        
        shifts = [self._shift_mapper.map_to_domain_model(store_shift) 
                  for store_shift in db_model.store_shifts]
        realograms = [self._realogram_mapper.map_to_domain_model(realogram) 
                      for realogram in db_model.snapshots]
        calibrations = [self._calibration_mapper.map_db_to_domain_model(calib)
                        for calib in db_model.calibrations]
        return Store(id=db_model.id,
                     login=db_model.login,
                     password_hash=db_model.password_hash,
                     is_office=db_model.is_office,
                     retail_id=db_model.retail_id,
                     shifts=shifts,
                     realograms=realograms,
                     name=db_model.name,
                     calibrations=calibrations)
    
    def map_to_db_model(self, domain_model: Store) -> StoreModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Store):
            raise ValueError(domain_model)
        store_shifts = [self._shift_mapper.map_to_db_model(domain_model, shift) for shift in domain_model.shifts]         
        return StoreModel(store_shifts=store_shifts,
                          login=domain_model.login,
                          password_hash=domain_model.password_hash,
                          retail_id=domain_model.retail_id,
                          is_office=domain_model.is_office,
                          name=domain_model.name)
        
    def map_to_response_model(self,
                              domain_model: Store
    ) -> StoreApiModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Store):
            raise ValueError(domain_model)
        return StoreApiModel(
            id=domain_model.id,
            name=domain_model.name,
            is_office=domain_model.is_office
        )
    
    def map_request_to_domain_model(self,
                                    request: StoreApiModel
    ) -> Store:
        if request is None: return None
        if not isinstance(request, StoreApiModel):
            raise ValueError(request)
        return Store(id=request.id,
                     is_office=request.is_office,
                     name=request.name)
    