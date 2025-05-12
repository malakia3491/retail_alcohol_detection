import traceback
from datetime import datetime
from Alc_Detection.Application.ImageGeneration.ProductMatrixImageGenerator import ProductMatrixImageGenerator
from fastapi import HTTPException, status

from Alc_Detection.Application.Mappers.PlanogramMapper import PlanogramMapper
from Alc_Detection.Domain.Entities import *
from Alc_Detection.Domain.Exceptions.Exceptions import ApprovePlanogramInDeclinedOrder, InvalidCalibrationBoxes
from Alc_Detection.Domain.Shelf.Calibration import Calibration
from Alc_Detection.Domain.Shelf.ProductMatrix.CalibrationBox import CalibrationBox
from Alc_Detection.Application.StoreInformation.Exceptions.Exceptions import (
     CalibrationException, IncorrectPlanogram,
     InvalidObjectId, InvalidPlanogramApprove, InvalidPlanogramUnapprove, PlanogramDoesNotHaveCalibration,
    ShelvingIsNotAssigned,
     ShelvingPlanogramIsAgreed
)
from Alc_Detection.Application.Requests.Requests import (
    ApprovePlanogramRequest,
    ProductMatrix as ProductMatrixModel)
from Alc_Detection.Application.Requests.Models import (
    Planogram as PlanogramModel,
    PlanogramDataResponse,
    PlanogramsResponse
)
from Alc_Detection.Application.Mappers.PlanogramOrderMapper import PlanogramOrderMapper
from Alc_Detection.Application.Mappers.ProductMatrixMapper import ProductMatrixMapper
from Alc_Detection.Persistance.Repositories.Repositories import *

class PlanogramResourcesService:
    def __init__(self,
                 image_generator: ProductMatrixImageGenerator,
                 store_repository: StoreRepository,
                 shelving_repository: ShelvingRepository,
                 planogram_order_repository: PlanogramOrderRepository,
                 person_repository: PersonRepository,
                 product_repository: ProductRepository,
                 planogram_order_mapper: PlanogramOrderMapper,
                 planogram_mapper: PlanogramMapper,
                 product_matrix_mapper: ProductMatrixMapper,):
        self._store_repository = store_repository
        self._shelving_repository = shelving_repository
        self._planogram_order_repository = planogram_order_repository
        self._person_repository = person_repository
        self._product_repository = product_repository
        
        self._planogram_mapper = planogram_mapper
        self._product_matrix_mapper = product_matrix_mapper
        self._planogram_order_mapper = planogram_order_mapper
        self._image_generator = image_generator
       
    async def get_planogram(
        self,
        order_id: str,
        planogram_id: str
    ) -> PlanogramModel:
        try:
            order = await self._planogram_order_repository.get(order_id)
            if order is None:
                raise InvalidObjectId()
            planogram = order.get_planogram(planogram_id)
            response = self._planogram_mapper.map_to_response_model(planogram)
            return response
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())
    
    async def get_calibrated_planogram(self, store_id: str, shelving_id: str) -> Planogram:
        try:
            store = await self._store_repository.get(store_id)   
            shelving = await self._shelving_repository.get(shelving_id)
                
            actual_planogram = store.get_actual_planogram_by(shelving)
            if not actual_planogram:
                raise PlanogramDoesNotHaveCalibration(shelving_id)
            calibration = store.get_planogram_calibration(actual_planogram.copy())
            actual_planogram.set_calibrations(calibration.calibrations_boxes)
            return actual_planogram
        except ValueError as ex:
            raise InvalidObjectId()
        except InvalidCalibrationBoxes as ex:
            raise CalibrationException(actual_planogram.id)              
       
    async def get_last_agreed_planograms(self) -> PlanogramsResponse:
        try:
            shelvings = await self._shelving_repository.get_all()
            orders = await self._planogram_order_repository.get_resolved_orders()  
            not_found_shelvings = set(shelvings)
            
            last_agreed_planograms: dict[Shelving, Planogram] = {}
            data: list[PlanogramDataResponse] = []         
            for order in orders:
                not_found_shelvings = not_found_shelvings.difference(set(last_agreed_planograms.keys()))
                for shelving in not_found_shelvings:                    
                    if order.contains(shelving):
                        planogram = order.get_agreed_planogram(shelving)
                        if planogram:
                            last_agreed_planograms[shelving] = planogram
                            data.append(PlanogramDataResponse(shelving_id=shelving.id, planogram_id=planogram.id, order_id=order.id))
                        else: continue
                    else: continue      
            response = PlanogramsResponse(
                planogram_data=data
            )                                           
            return response
        except Exception as ex:
            raise ex
    
    async def calibrate_store_planogram(self,
                                        person_id: str,
                                        store_id: str,
                                        order_id: str,
                                        shelving_id: str,
                                        calibration_boxes: list[CalibrationBox],
                                        path: str
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
                agreed_not_calibrated_planogram.img_src = path
                await self._planogram_order_repository.update_planogram(
                    order_id=order_id,
                    planogram_id=agreed_not_calibrated_planogram.id,
                    data={ "img_src": path }
                )
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
            if not isinstance(products, list): products = [*products]
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
            planogram.img_src = self._image_generator.generate(
                id_name=planogram.id,
                product_matrix=planogram.product_matrix,
                obj_type=Planogram
            )                  
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__()) 
    
    async def approve_planogram(self, request: ApprovePlanogramRequest) -> str:
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
        
    async def unapprove_planogram(self, request: ApprovePlanogramRequest) -> str:
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
           