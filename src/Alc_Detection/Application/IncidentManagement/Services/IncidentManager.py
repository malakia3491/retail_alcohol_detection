from datetime import datetime

from Alc_Detection.Application.IncidentManagement.Interfaces.Messenger import Messenger
from Alc_Detection.Application.IncidentManagement.Settings import Settings
from Alc_Detection.Application.StoreInformation.Services.StoreServiceFacade import StoreService
from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation
from Alc_Detection.Domain.Shelf.DeviationManagment.EmptyDeviation import EmptyDeviation
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Shelf.DeviationManagment.IncongruityDeviation import incongruityDeviation
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Application.Notification.Message import Message
from Alc_Detection.Domain.Store.PersonManagment.Permition import Permition
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Persistance.Repositories.PostRepository import PostRepository
from Alc_Detection.Persistance.Repositories.StoreRepository import StoreRepository

class IncidentManager:
    def __init__(self,
                 store_service: StoreService,
                 store_repository: StoreRepository,
                 post_repository: PostRepository,
                 settings: Settings,
                 messenger: Messenger
    ):
        self._store_service = store_service
        self._store_repository = store_repository
        self._post_repository = post_repository
        self._settings = settings
        self._messenger = messenger        
        
    async def on_start(self):
        posts = await self._post_repository.get_all()
        self._regular_posts = []
        self._administrative_posts = []
        for post in posts:
            if Permition("layout:incidents:standard") in post.permitions:
                self._regular_posts.append(post)
            elif Permition("layout:incidents:no-product") in post.permitions:
                self._administrative_posts.append(post)
    
    async def handle_realogram(
        self,
        store: Store,
        realogram: Realogram
    ) -> None:
        now = datetime.now()  
        shift = store.actual_shift
        unresolved_incidents = shift.get_unresolved_incidents_by_shelving(realogram.shelving)
        print(f"ВСЕ ИНЦИДЕНТЫ {shift.incidents}")
        print(f"Нерешённые инциденты {unresolved_incidents}")   
        print("Deviations", realogram.deviation_count)                    
        if realogram.deviation_count < 0:
            for incident in unresolved_incidents:
                incident.resolve(now) 
        else:
            print("SHIFT", shift)
            update_incidents: list[Incident] = []            
            for incident in unresolved_incidents:
                for deviation in incident.deviations:
                    if not deviation._product_box in realogram.empties and \
                       not deviation._product_box in realogram.inconsistencies:
                        deviation.elimination_time = now
                        if incident not in update_incidents:
                            update_incidents.append(incident)
                                                                                                                    
            new_incidents = await self._create_incidents(
                store=store,
                shift=shift,
                realogram=realogram,
                unresolved_incidents=unresolved_incidents
            )
            
            print("New incidents", new_incidents)
            if len(update_incidents) > 0:
                deviations = []
                [deviations.extend(incident.deviations) for incident in update_incidents]
                await self._store_repository.update_detections_elimination_time(
                    store, now, *deviations
                )
                await self._store_repository.update_incidents_elimination_time(
                    store, *update_incidents)
            if len(new_incidents) > 0:
                shift.add_incidents(*new_incidents)
                await self._store_repository.add_incident(
                    store, shift, *new_incidents)
            
                messages = [Message(realogram_img_src=realogram.image_source,
                                    planogram_img_src=realogram.planogram.img_src,
                                    incident=incident,
                                    user_ids=[person.telegram_id for person in incident.responsible_employees]
                            ) for incident in new_incidents]
                print(messages)
                # for message in messages:
                #     self._messenger.send(
                #         ids=[],
                #         message=message
                #     )                                        
    
    async def _create_incidents(
        self,
        store: Store,
        shift: Shift,
        realogram: Realogram,
        unresolved_incidents: list[Incident]
    ) -> list[Incident]:
        empty_incident, admin_incident = await self._handle_realogram_empties(
            store=store,
            shift=shift,
            realogram=realogram,
            unresolved_incidents=unresolved_incidents
        )
        inconsistencies_incident = self._handle_realogram_incongruity(
            realogram=realogram,
            shift=shift,
            unresolved_incidents=unresolved_incidents
        )               
        new_incidents = []
        if admin_incident: new_incidents.append(admin_incident)                
        if empty_incident: new_incidents.append(empty_incident)
        if inconsistencies_incident: new_incidents.append(inconsistencies_incident)                  
        return new_incidents                 
                     
    async def _handle_realogram_empties(
        self,
        store: Store,
        shift: Shift,
        realogram: Realogram,
        unresolved_incidents: list[Incident],
    ) -> Incident:
        deviations: list[EmptyDeviation] = []
        not_enough_product_deviations: list[EmptyDeviation] = []
        for deviation in realogram.empties:
            print("current deviation:", deviation)                            
            for incident in unresolved_incidents:
                if not incident.contains(deviation):
                    actual_product_count = await self._store_service.get_actual_product_count(
                        store=store,
                        product=deviation.product
                    )
                    plan_product_count = realogram.planogram.get_need_product_count(
                        product=deviation.product
                    ) 
                    deviation.is_enough_product = actual_product_count >= plan_product_count
                    if not deviation.is_enough_product:
                        not_enough_product_deviations.append(deviation)                        
                    else: deviations.append(deviation)   
            if not unresolved_incidents:
                actual_product_count = await self._store_service.get_actual_product_count(
                    store=store,
                    product=deviation.product
                )
                plan_product_count = realogram.planogram.get_need_product_count(
                    product=deviation.product
                ) 
                deviation.is_enough_product = actual_product_count >= plan_product_count
                if not deviation.is_enough_product:
                    not_enough_product_deviations.append(deviation)                        
                else: deviations.append(deviation)   
        
        admin_incident = None
        new_incident = None
        if len(deviations) >= self._settings.FACES_COUNT:
            employees = shift.get_actual_employees_by(self._regular_posts)
            new_incident = Incident(
                send_time=datetime.now(),
                realogram=realogram,
                deviations=deviations,
                responsible_employees=employees)
        if len(not_enough_product_deviations) > 0:
            administators = shift.get_actual_employees_by(self._administrative_posts)
            admin_incident = Incident(
                send_time=datetime.now(),
                realogram=realogram,
                deviations=not_enough_product_deviations,
                responsible_employees=administators)        
        return new_incident, admin_incident  
    
    def _handle_realogram_incongruity(
        self,
        shift: Shift,
        realogram: Realogram,
        unresolved_incidents: list[Incident],
    ) -> Incident:
        deviations: list[incongruityDeviation] = []
        for deviation in realogram.inconsistencies:                            
            for incident in unresolved_incidents:
                if not incident.contains(deviation):                   
                    deviations.append(deviation)
            if not unresolved_incidents:
                deviations.append(deviation)
                
        if len(deviations) >= self._settings.FACES_COUNT:
            employees = shift.get_actual_employees_by(self._regular_posts)
            new_incident = Incident(
                send_time=datetime.now(),
                realogram=realogram,
                deviations=deviations,
                responsible_employees=employees)
            return new_incident
        return None     