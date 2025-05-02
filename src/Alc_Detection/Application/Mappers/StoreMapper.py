from Alc_Detection.Application.Mappers.CalibrationMapper import CalibrationMapper
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Application.Requests.Models import Store as StoreResponseModel
from Alc_Detection.Persistance.Models.Models import Store as StoreModel 

class StoreMapper:    
    def __init__(self,
                 person_mapper: PersonMapper, 
                 calibration_mapper: CalibrationMapper):
        self._calibration_mapper = calibration_mapper
        self._person_mapper = person_mapper
    
    def map_to_domain_model(self, db_model: StoreModel) -> Store:
        if db_model is None: return None
        if not isinstance(db_model, StoreModel):
            raise ValueError(db_model)
        persons = [self._person_mapper.map_to_domain_model(person)
                   for person in db_model.persons]
        calibrations = [self._calibration_mapper.map_db_to_domain_model(calib)
                        for calib in db_model.calibrations]
        return Store(id=db_model.id,
                     name=db_model.name,
                     calibrations=calibrations,
                     persons=persons)
    
    def map_to_db_model(self, domain_model: Store) -> StoreModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Store):
            raise ValueError(domain_model)
        return StoreModel(id=domain_model.id,
                          name=domain_model.name)
        
    def map_to_response_model(self,
                              domain_model: Store
    ) -> StoreResponseModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Store):
            raise ValueError(domain_model)
        raise NotImplementedError()
        return None
    
    def map_request_to_domain_model(self,
                                    request: StoreResponseModel
    ) -> Store:
        if request is None: return None
        if not isinstance(request, StoreResponseModel):
            raise ValueError(request)
        return Store(id=request.id,
                     name=request.name)
    