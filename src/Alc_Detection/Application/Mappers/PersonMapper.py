from Alc_Detection.Domain.Entities import Person
from Alc_Detection.Application.Requests.Models import Person as PersonResponseModel
from Alc_Detection.Domain.Store.PersonManagment.Permition import Permition
from Alc_Detection.Persistance.Models.Models import Person as PersonModel

class PersonMapper:
    def map_to_domain_model(self, db_model: PersonModel) -> Person:
        if db_model is None: return None
        if not isinstance(db_model, PersonModel):
            raise ValueError(db_model)        
        
        return Person(id=db_model.id,
                      retail_id=db_model.retail_id,
                      name=db_model.name,
                      email=db_model.email,
                      telegram_id=db_model.telegram_id,
                      password_hash=db_model.password_hash,
                      is_store_worker=db_model.is_store_worker,
                      is_active=db_model.is_active)
            
    def map_to_db_model(self, domain_model: Person) -> PersonModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Person):
            raise ValueError(domain_model)
        return PersonModel(name=domain_model.name,
                           retail_id=domain_model.retail_id,
                           telegram_id=domain_model.telegram_id,
                           email=domain_model.email,
                           is_store_worker=domain_model.is_store_worker)
        
    def map_to_response_model(self,
                              domain_model: Person
    ) -> PersonResponseModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Person):
            raise ValueError(domain_model)
        return PersonResponseModel(id = domain_model.id,
                                   email = domain_model.email,
                                   name = domain_model.name)