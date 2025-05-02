from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Store.PlanogramOrder import PlanogramOrder
from Alc_Detection.Domain.Store.Shelving import Shelving
from Alc_Detection.Application.Mappers.PlanogramMapper import PlanogramMapper
from Alc_Detection.Application.Mappers.ShelvingMapper import ShelvingMapper
from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Application.Requests.Models import PlanogramOrder as PlanogramOrderResponceModel
from Alc_Detection.Persistance.Models.Models import PlanogramOrder as PlanogramOrderModel 
from Alc_Detection.Persistance.Models.Models import ShelvingPlanogramOrder

class PlanogramOrderMapper:
    def __init__(self,
                 person_mapper: PersonMapper,
                 shelving_mapper: ShelvingMapper,
                 planogram_mapper: PlanogramMapper):
        self._person_mapper = person_mapper
        self._shelving_mapper = shelving_mapper
        self._planogram_mapper = planogram_mapper
    
    def map_to_domain_model(self, db_model: PlanogramOrderModel) -> PlanogramOrder:
        if db_model is None: return None
        if not isinstance(db_model, PlanogramOrderModel):
            raise ValueError(db_model)
        person = self._person_mapper.map_to_domain_model(db_model.person)
        assignments: dict[Shelving, list[Planogram]] = {}            
        for shelving_assignment in db_model.shelving_planogram_orders:
            shelving = self._shelving_mapper.map_to_domain_model(shelving_assignment.shelving)
            if shelving not in assignments.keys():
                assignments[shelving] = []
            for planogramModel in shelving_assignment.planograms:
                assignments[shelving].append(self._planogram_mapper.map_to_domain_model(planogramModel))

        order = PlanogramOrder(id=db_model.id,
                              author=person,
                              create_date=db_model.order_date,
                              develop_date=db_model.dev_date,
                              implementation_date=db_model.inc_date,
                              shelvings=assignments.keys())
        order.fill_order(assignments=assignments)
        return order
    
    def map_to_db_model(self, domain_model: PlanogramOrder) -> PlanogramOrderModel:
        if domain_model is None: return None
        if not isinstance(domain_model, PlanogramOrder):
            raise ValueError(domain_model)
                  
        order = PlanogramOrderModel(person_id=domain_model.author.id,
                                    order_date=domain_model.create_date,
                                    dev_date=domain_model.develop_date,
                                    inc_date=domain_model.implementation_date,)   

        order.shelving_planogram_orders = [
            ShelvingPlanogramOrder(shelving_id=shelving.id) 
            for shelving in domain_model.shelvings
        ]                                
        return order
    
    def map_to_response_model(self,
                              domain_model: PlanogramOrder
    ) -> PlanogramOrderResponceModel:
        author = self._person_mapper.map_to_response_model(domain_model.author)
        shelving_assignments = {}
        shelvings = []
        for shelving_key, planograms in domain_model.shelving_assignments.items():
            shelving = self._shelving_mapper.map_to_response_model(shelving_key)            
            shelvings.append(shelving)
            shelving_assignments[shelving.id] = [self._planogram_mapper.map_to_response_model(planogram)
                                              for planogram in planograms]   
        order = PlanogramOrderResponceModel(id = domain_model.id,
                                            author = author,
                                            shelving_assignments = shelving_assignments,
                                            create_date = domain_model.create_date,
                                            develop_date = domain_model.develop_date,
                                            implementation_date = domain_model.implementation_date,
                                            shelvings=shelvings,
                                            is_declined = domain_model.is_declined)
        return order
         