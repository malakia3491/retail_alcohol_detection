import traceback
from datetime import datetime
from fastapi import HTTPException, status

from Alc_Detection.Domain.Entities import *
from Alc_Detection.Domain.Exceptions.Exceptions import ApprovePlanogramInDeclinedOrder, InvalidCalibrationBoxes
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Shelf.ProductMatrix.CalibrationBox import CalibrationBox
from Alc_Detection.Domain.Store.PlanogramOrder import PlanogramOrder
from Alc_Detection.Application.Extentions.Utils import between
from Alc_Detection.Application.StoreInformation.Exceptions.Exceptions import \
    (CalibrationException, IncorrectPlanogram, IncorrectUpdateData,
     InvalidObjectId, InvalidPlanogramApprove, InvalidPlanogramUnapprove,
     PersonIsNotWorkerAlready, PlanogramOrderIsNotResolved, ShelvingIsNotAssigned,
     ShelvingPlanogramIsAgreed)
from Alc_Detection.Application.Requests.Requests import \
(AddPersonsRequest, AddProductsRequest, AddShelvingsRequest,
 AddStoresRequest, ApprovePlanogramRequest, DismissPersonRequest,
 ProductMatrix as ProductMatrixModel, UpdatePersonRequest, UpdatePersonsRequest)
from Alc_Detection.Application.Mappers.PlanogramOrderMapper import PlanogramOrderMapper
from Alc_Detection.Application.Mappers.ProductMatrixMapper import ProductMatrixMapper
from Alc_Detection.Application.Requests.Models import PlanogramOrdersResponse
from Alc_Detection.Persistance.Repositories.Repositories import *

class StoreService:
    def __init__(self,
                 store_repository: StoreRepository,
                 shelving_repository: ShelvingRepository,
                 planogram_order_repository: PlanogramOrderRepository,
                 person_repository: PersonRepository,
                 product_repository: ProductRepository,
                 planogram_order_mapper: PlanogramOrderMapper,
                 product_matrix_mapper: ProductMatrixMapper):
        self._store_repository = store_repository
        self._shelving_repository = shelving_repository
        self._planogram_order_repository = planogram_order_repository
        self._person_repository = person_repository
        self._product_repository = product_repository
        self._product_matrix_mapper = product_matrix_mapper
        self._planogram_order_mapper = planogram_order_mapper
    
    async def get_actual_store_shift(
        self,
        store: Store,
        date: datetime
    ) -> None:
        raise NotImplementedError()
    
    async def get_actual_product_count(
        self,
        store: Store,
        product: Product
    ) -> int:
        raise NotImplementedError()
    
    async def get_calibrated_planogram(self, store_id: str, shelving_id: str) -> Planogram:
        try:
            store = await self._store_repository.get(store_id)   
            shelving = await self._shelving_repository.get(shelving_id)
                
            actual_planogram = store.get_actual_planogram_by(shelving).copy()
            calibration = store.get_planogram_calibration(actual_planogram)
            actual_planogram.set_calibrations(calibration.calibrations_boxes)
            return actual_planogram
        except ValueError as ex:
            raise InvalidObjectId()
        except InvalidCalibrationBoxes as ex:
            raise CalibrationException(actual_planogram.id)              
       
    async def get_last_agreed_planograms(self) -> list[Planogram]:
        try:
            shelvings = await self._shelving_repository.get_all()
            orders = await self._planogram_order_repository.get_resolved_orders()  
            not_found_shelvings = set(shelvings)
            
            last_agreed_planograms: dict[Shelving, Planogram] = {}            
            for order in orders:
                not_found_shelvings = not_found_shelvings.difference(set(last_agreed_planograms.keys()))
                for shelving in not_found_shelvings:                    
                    if order.contains(shelving):
                        planogram = order.get_agreed_planogram(shelving)
                        if planogram:
                            last_agreed_planograms[shelving] = planogram
                        else: continue
                    else: continue                                         
            return last_agreed_planograms
        except Exception as ex:
            raise ex
    
    async def calibrate_store_planogram(self,
                                        person_id: str,
                                        store_id: str,
                                        order_id: str,
                                        shelving_id: str,
                                        calibration_boxes: list[CalibrationBox]
    ) -> str:
        try:
            creator = await self._person_repository.get(person_id)
            store = await self._store_repository.get(store_id)
            agreed_not_calibrated_planogram = await self.get_agreed_planogram(shelving_id=shelving_id,
                                                                              order_id=order_id)                              
            if agreed_not_calibrated_planogram is not None and agreed_not_calibrated_planogram.is_valid_calibrations(calibration_boxes):
                calibration = Calibration(date=datetime.now(),
                                          creator=creator,
                                          planogram=agreed_not_calibrated_planogram,
                                          calibration_boxes=calibration_boxes)
                result = await self._store_repository.add_calibration(store=store,
                                                                      calibration=calibration)
                message = f"Было добавлено {result} колибровок. Координаты для товаров были добавлены."
            else:
                message = f"Данные координаты нельзя установить для планограммы на стеллаж {shelving_id} по приказу {store_id} "
            return message
        except Exception as ex:
            raise ex    
                           
    async def get_agreed_planogram(self, order_id: str, shelving_id: str) -> Planogram:
        try:
            shelving = await self._shelving_repository.get(shelving_id)
            order = await self._planogram_order_repository.get(order_id)
            
            planogram = order.get_agreed_planogram(shelving)
            return planogram
        except Exception as ex:
            raise ex
        
    async def add_stores(self, request: AddStoresRequest) -> str:
        try:
            stores = [Store(name=store.name) for store in request.stores]
            count_added_records = await self._store_repository.add(*stores)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     
    
    async def add_products(self, request: AddProductsRequest) -> str:
        try:
            products = [Product(name=product.name) for product in request.products]
            count_added_records = await self._product_repository.add(*products)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     
    
    async def add_shelvings(self, request: AddShelvingsRequest) -> str:
        try:
            products = [Shelving(name=shelving.name,
                                 shelves_count=shelving.shelves_count)
                        for shelving in request.shelvings]
            count_added_records = await self._shelving_repository.add(*products)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     
    
    async def add_persons(self, request: AddPersonsRequest) -> str:
        try:
            persons = []
            for request_person in request.persons:
                store = None
                if not request_person.store_id  is None:                    
                    store = await self._store_repository.get(request_person.store_id)                                        
                    person = Person(name=request_person.name,
                                    store=store,
                                    telegram_id=request_person.telegram_id)
                    store.add_person(person)
                else:
                    person = Person(name=request_person.name,
                                    telegram_id=request_person.telegram_id)
                persons.append(person)
            count_added_records = await self._person_repository.add(*persons)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     
        
    async def dismiss_employee(self, request: DismissPersonRequest) -> str:
        field = "is_worker"             
        person_data = {field: False}        
        try:
            person = await self._person_repository.get(request.person_id)
            if not person.is_worker:
                raise PersonIsNotWorkerAlready(person.name)
                            
            record_count = await self._person_repository.update(request.person_id, person_data)
            return f"Succsessfully. Updated {record_count} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())     
        
    async def add_planogram(self,
                            order_id: str,
                            shelving_id: str,
                            author_id: str,
                            planogram_matrix: ProductMatrixModel) -> None:
        try:
            order = await self._planogram_order_repository.get(order_id)
            shelving = await self._shelving_repository.get(shelving_id)
            author = await self._person_repository.get(author_id)

            if not order.contains(shelving=shelving):
                raise ShelvingIsNotAssigned(order_id=order.id,
                                            order_create_date=order.create_date,
                                            shelving_name=shelving.name)
                        
            if order.is_shelving_resolved(shelving=shelving):
                raise ShelvingPlanogramIsAgreed(order_id=order.id,
                                                order_create_date=order.create_date,
                                                shelving_name=shelving.name)
                        
            if shelving.shelves_count != len(planogram_matrix.shelfs):
                raise IncorrectPlanogram(shelving_name=shelving.name,
                                         shelving_shelves_count=shelving.shelves_count,
                                         shelfs_len=len(planogram_matrix.shelfs))
            
            products = await self._product_repository.get(*[product.product_id for product in planogram_matrix.products])
            product_matrix, product_count = \
                self._product_matrix_mapper.map_response_to_domain_model(request_model=planogram_matrix,
                                                                         products=products)              
            planogram = Planogram(
                shelving=shelving,
                author=author,
                create_date=datetime.now(),
                product_count=product_count,
                product_matrix=product_matrix
            )          
            await self._planogram_order_repository.add_planogram(order_id=order.id, 
                                                                 new_planogram=planogram)
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__()) 
    
    async def get_planogram_orders(self,
                                   date_start: datetime,
                                   date_end: datetime) -> list[PlanogramOrder]:
        try:
            orders = await self._planogram_order_repository.get_all()
            result = []
            for order in orders:
                if between(date=order.create_date,
                           start=date_start.date(),
                           end=date_end.date()):                    
                    result.append(order)
            response = PlanogramOrdersResponse(planogram_orders=
                        [self._planogram_order_mapper.map_to_response_model(order)
                        for order in result])
            return response            
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__()) 
    
    async def create_planogram_order(self,
                                     person_id: str,
                                     shelving_ids: list[str],
                                     develop_date: datetime,
                                     implementation_date: datetime
    ) -> str:        
        try:
            shelving_ids = list(set(shelving_ids))
            order_author = await self._person_repository.get(person_id)
            shelvings = [await self._shelving_repository.get(shelving_id) for shelving_id in shelving_ids]
            new_planogram_order = PlanogramOrder(author=order_author,
                                                 create_date=datetime.now(),
                                                 develop_date=develop_date,
                                                 implementation_date=implementation_date)            
            not_resolved_orders = await self._planogram_order_repository.get_not_resolved_orders()
            for shelving in shelvings:
                for order in not_resolved_orders:
                    if order.contains(shelving):                          
                        raise PlanogramOrderIsNotResolved(order_id=order.__class__,
                                                        order_create_date=order.create_date)
                new_planogram_order.add_shelving_assignment(shelving=shelving)     
            added_records_count = await self._planogram_order_repository.add(new_planogram_order)      
            message = f"Succsessfully. Added {added_records_count} records."
            return message                                                          
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__()) 
            
    async def decline_planogram_order(self,
                                      person_id: str,
                                      order_id: str) -> None:
        try:
            person = await self._person_repository.get(person_id)
            order = await self._planogram_order_repository.get(order_id)
            
            if order.decline():
                message = f"Succsessfully. Order is declined"
            else: message = f"Unsuccsessfully. Order is not declined"            
            return message
        except Exception as ex:
            print(traceback.format_exc())
            raise ex
    
    async def approve_planogram(self,
                                request: ApprovePlanogramRequest
    ) -> str:
        try:
            approver = await self._person_repository.get(request.approver_id)
            order = await self._planogram_order_repository.get(request.order_id)
            order.approve_planogram(approver=approver,
                                    date=datetime.now(),
                                    planogram_id=request.planogram_id)
            data = {
                "approver_id": approver.id,
                "approval_date": datetime.now()
            }                  
            await self._planogram_order_repository.update_planogram(order_id=order.id,
                                                                    planogram_id=request.planogram_id,
                                                                    data=data)  
            message = f"Succsessfully. Planogram is approved"
            return message
        except ApprovePlanogramInDeclinedOrder as ex:
            print(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Order {request.order_id} is declined")
        except ValueError as ex:
            print(traceback.format_exc())
            raise InvalidPlanogramApprove(request.planogram_id)
        except Exception as ex:
            print(traceback.format_exc())
            raise ex
        
    async def unapprove_planogram(self,
                                  request: ApprovePlanogramRequest
    ) -> str:
        try:
            approver = await self._person_repository.get(request.approver_id)
            order = await self._planogram_order_repository.get(request.order_id)
            order.unapprove_planogram(date=datetime.now(),
                                      planogram_id=request.planogram_id)
            data = {
                "approver_id": None,
                "approval_date": None
            }                  
            await self._planogram_order_repository.update_planogram(order_id=order.id,
                                                                    planogram_id=request.planogram_id,
                                                                    data=data)  
            message = f"Succsessfully. Planogram is unapproved"
            return message
        except ApprovePlanogramInDeclinedOrder as ex:
            print(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f"Order {request.order_id} is declined")
        except ValueError as ex:
            print(traceback.format_exc())
            raise InvalidPlanogramUnapprove(request.planogram_id)
        except Exception as ex:
            print(traceback.format_exc())
            raise ex
           