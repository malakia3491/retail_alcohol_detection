from Alc_Detection.Domain.Store.PlanogramOrder import Shelving
from Alc_Detection.Application.Requests.Models import Shelving as ShelvingResponseModel
from Alc_Detection.Persistance.Models.Models import Shelving as ShelvingModel 

class ShelvingMapper:    
    def map_to_domain_model(self, db_model: ShelvingModel) -> Shelving:
        if db_model is None: return None
        if not isinstance(db_model, ShelvingModel):
            raise ValueError(db_model)
        return Shelving(id=db_model.id,
                        retail_id=db_model.retail_id,
                        name=db_model.name,
                        shelves_count=db_model.shelves_count)
    
    def map_to_db_model(self, domain_model: Shelving) -> ShelvingModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Shelving):
            raise ValueError(domain_model)
        return ShelvingModel(id=domain_model.id,
                             name=domain_model.name,
                             retail_id=domain_model.retail_id,
                             shelves_count=domain_model.shelves_count)
        
    def map_to_response_model(self,
                              domain_model: Shelving
    ) -> ShelvingResponseModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Shelving):
            raise ValueError(domain_model)
        return ShelvingResponseModel(id = domain_model.id,
                                     shelves_count= domain_model.shelves_count,
                                     name = domain_model.name)