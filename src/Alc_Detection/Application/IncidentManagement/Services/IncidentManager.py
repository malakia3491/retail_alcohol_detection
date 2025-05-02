from datetime import datetime

from Alc_Detection.Application.IncidentManagement.Interfaces.Messenger import Messenger
from Alc_Detection.Application.IncidentManagement.Settings import Settings
from Alc_Detection.Application.StoreInformation.Services.StoreService import StoreService
from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation
from Alc_Detection.Domain.Shelf.DeviationManagment.EmptyDeviation import EmptyDeviation
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Shelf.DeviationManagment.IncongruityDeviation import incongruityDeviation
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Persistance.Repositories.StoreRepository import StoreRepository

class IncidentManager:
    def __init__(self,
                 store_service: StoreService,
                 store_repository: StoreRepository,
                 settings: Settings,
                 messenger: Messenger=None,
    ):
        self._store_service = store_service
        self._store_repository = store_repository
        self._settings = settings
        self._messenger = messenger        
    
    async def handle_realogram(
        self,
        store: Store,
        realogram: Realogram
    ) -> None:
        unresolved_incidents = store.unresolved_incidents                         
        if realogram.deviation_count < 0:
            for incident in unresolved_incidents:
                incident.resolve(datetime.now().time()) 
        else:
            now = datetime.now()       
            shift = await self._store_service.get_actual_store_shift(
                store=store,
                date=now.date()
            )
            update_incidents = []            
            for incident in unresolved_incidents:
                for deviation in incident.deviations:
                    if not deviation._product_box in realogram.empties and \
                       not deviation._product_box in realogram.inconsistencies:
                        deviation.elimination_time = now.time()
                        if incident not in update_incidents:
                            update_incidents.append(incident)
                                                                                                                    
            new_incidents = await self._create_incidents(
                store=store,
                realogram=realogram,
                unresolved_incidents=unresolved_incidents
            )
            store.add_incident(*new_incidents)
            await self._store_repository.add_incident(
                store=store, *new_incidents)
            await self._store_repository.update_incidents(
                store=store, *update_incidents)
            
            messages = self._create_messages(incidents=new_incidents)
            for message in messages:
                self._messenger.send(
                    ids=[],
                    message=message
                )
                                              
    def _create_messages(
        self,
        incidents: list[Incident]
    ) -> str:
        pass
    
    async def _create_incidents(
        self,
        store: Store,
        realogram: Realogram,
        unresolved_incidents: list[Incident]
    ) -> list[Incident]:
        empty_incident = await self._handle_realogram_empties(
            store=store,
            realogram=realogram,
            unresolved_incidents=unresolved_incidents
        )
        inconsistencies_incident = self._handle_realogram_incongruity(
            realogram=realogram,
            unresolved_incidents=unresolved_incidents
        )               
        new_incidents = []                
        if empty_incident: new_incidents.append(empty_incident)
        if inconsistencies_incident: new_incidents.append(inconsistencies_incident)                  
        return new_incidents                 
                     
    async def _handle_realogram_empties(
        self,
        store: Store,
        realogram: Realogram,
        unresolved_incidents: list[Incident],
    ) -> Incident:
        deviations: list[EmptyDeviation] = []
        for product_box in realogram.empties:                            
            for incident in unresolved_incidents:
                deviation = EmptyDeviation(
                    product_box=product_box
                )
                if not incident.contains(deviation):
                    actual_product_count = await self._store_service.get_actual_product_count(
                        store=store,
                        product=product_box.product
                    )
                    plan_product_count = realogram.planogram.get_need_product_count(
                        product=product_box.product
                    ) 
                    deviation.is_enough_product = actual_product_count >= plan_product_count                        
                    deviations.append(deviation)   
        
        if len(deviations) >= self._settings.FACES_COUNT:
            new_incident = Incident(
                send_time=datetime.now().time(),
                realogram=realogram,
                deviations=deviations,
                shift=None)
            return new_incident
        return None  
    
    def _handle_realogram_incongruity(
        self,
        realogram: Realogram,
        unresolved_incidents: list[Incident],
    ) -> Incident:
        deviations: list[incongruityDeviation] = []
        for product_box in realogram.empties:                            
            for incident in unresolved_incidents:
                deviation = EmptyDeviation(
                    product_box=product_box
                )
                if not incident.contains(deviation):                   
                    deviations.append(deviation)
       
        if len(deviations) >= self._settings.FACES_COUNT:
            new_incident = Incident(
                send_time=datetime.now().time(),
                realogram=realogram,
                deviations=deviations,
                shift=None)
            return new_incident
        return None     