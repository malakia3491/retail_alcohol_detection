from Alc_Detection.Domain.Entities import Person
from Alc_Detection.Application.Requests.Models import Person as PersonResponseModel
from Alc_Detection.Persistance.Models.Models import Person as PersonModel

class PersonMapper:
    def map_to_domain_model(self, db_model: PersonModel) -> Person:
        if db_model is None: return None
        if not isinstance(db_model, PersonModel):
            raise ValueError(db_model)
        return Person(id=db_model.id,
                      name=db_model.name,
                      telegram_id=db_model.telegram_id,
                      password_hash=db_model.password_hash,
                      is_worker=db_model.is_worker,
                      is_active=db_model.is_active)
            
    def map_to_db_model(self, domain_model: Person) -> PersonModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Person):
            raise ValueError(domain_model)
        store_id = None if domain_model.store is None else domain_model.store.id
        return PersonModel(name=domain_model.name,
                           telegram_id=domain_model.telegram_id,
                           is_worker=domain_model.is_worker,
                           store_id=store_id)
        
    def map_to_response_model(self,
                              domain_model: Person
    ) -> PersonResponseModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Person):
            raise ValueError(domain_model)
        return PersonResponseModel(id = domain_model.id,
                                   name = domain_model.name)