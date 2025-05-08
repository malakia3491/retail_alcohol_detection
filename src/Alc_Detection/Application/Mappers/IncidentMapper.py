from Alc_Detection.Application.Mappers.PersonMapper import PersonMapper
from Alc_Detection.Application.Mappers.ProductMapper import ProductMapper
from Alc_Detection.Application.Mappers.RealogramMapper import RealogramMapper
from Alc_Detection.Domain.Shelf.DeviationManagment.IncongruityDeviation import incongruityDeviation
from Alc_Detection.Domain.Shelf.DeviationManagment.EmptyDeviation import EmptyDeviation
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Persistance.Models.Models import Incident as IncidentModel
from Alc_Detection.Persistance.Models.ShelfDetection.RealogramSnapshot import RealogramSnapshot

class IncidentMapper:
    def __init__(
        self,
        product_mapper: ProductMapper,
        person_mapper: PersonMapper,
        realogram_mapper: RealogramMapper,
    ):
        self._product_mapper = product_mapper
        self._person_mapper = person_mapper
        self._realogram_mapper = realogram_mapper     
    
    def map_db_to_domain(self, db_model: IncidentModel) -> Incident:
        if db_model is None: return None
        if not isinstance(db_model, IncidentModel):
            raise ValueError(db_model)
        persons = [self._person_mapper.map_to_db_model(inc_person.person)
                   for inc_person in db_model.persons]
        
        deviations = []
        for detection in db_model.detections:
            product = self._product_mapper.map_to_domain_model(detection.product)
            if(detection.is_empty):
                deviation = EmptyDeviation(
                    product_box=ProductBox(
                        id=detection.id,
                        product=product,
                        is_empty=True,
                        is_incorrect_position=False),                        
                    elimination_time=detection.elimination_time)
            elif(detection.is_incorrect_pos):
                deviation = incongruityDeviation(
                    product_box=ProductBox(
                        id=detection.id,
                        product=product,
                        is_empty=True,
                        is_incorrect_position=False),
                    elimination_time=detection.elimination_time,
                    right_product=self._product_mapper.map_to_domain_model(detection.right_product))
            deviations.append(deviation)
                
        incident = Incident(
            send_time=db_model.send_time,
            realogram=self._realogram_mapper.map_to_domain_model(db_model.detections[0].snapshot),
            deviations=deviations,
            responsible_employees=persons,
            id=db_model.id,
        )
        return incident