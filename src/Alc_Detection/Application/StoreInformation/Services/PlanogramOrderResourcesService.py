import math
import traceback
from datetime import datetime
from fastapi import HTTPException, status

from Alc_Detection.Application.Requests.Responses import PlanogramOrdersPageResponse, PlanogramOrdersResponse
from Alc_Detection.Domain.Entities import *
from Alc_Detection.Domain.Store.PlanogramOrder import PlanogramOrder
from Alc_Detection.Application.Extentions.Utils import between
from Alc_Detection.Application.StoreInformation.Exceptions.Exceptions import (
     InvalidObjectId, PlanogramOrderIsNotResolved
)
from Alc_Detection.Application.Mappers.PlanogramOrderMapper import PlanogramOrderMapper
from Alc_Detection.Persistance.Repositories.Repositories import *

class PlanogramOrderResourcesService:
    def __init__(self,
                 shelving_repository: ShelvingRepository,
                 planogram_order_repository: PlanogramOrderRepository,
                 person_repository: PersonRepository,
                 planogram_order_mapper: PlanogramOrderMapper):
        self._shelving_repository = shelving_repository
        self._planogram_order_repository = planogram_order_repository
        self._person_repository = person_repository
        self._planogram_order_mapper = planogram_order_mapper
    
    async def get_page_not_resolved_planogram_orders(
        self,
        page: int,
        page_size: int
    ) -> PlanogramOrdersPageResponse:
        try:
            orders = await self._planogram_order_repository.get_not_resolved_orders()        
            start = page * page_size
            end = start + page_size
            result = []
            for order in orders[start:end]:
                response = self._planogram_order_mapper.map_to_response_model(order)
                result.append(response)
            response = PlanogramOrdersPageResponse(
                planogram_orders=result,
                page=page,
                page_size=page_size,
                total_count= math.ceil(len(orders) / page_size)
            )
            return response
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())
    
    async def get_page_planogram_orders(
        self,
        page: int,
        page_size: int
    ) -> PlanogramOrdersPageResponse:
        try:
            orders = await self._planogram_order_repository.get_all()
            start = page * page_size
            end = start + page_size
            result = []
            for order in orders[start:end]:
                response = self._planogram_order_mapper.map_to_response_model(order)
                result.append(response)
            response = PlanogramOrdersPageResponse(
                planogram_orders=result,
                page=page,
                page_size=page_size,
                total_count= math.ceil(len(orders) / page_size)
            )
            return response
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())
    
    async def get_planogram_order(self, order_id: str) -> PlanogramOrder:
        try:
            order = await self._planogram_order_repository.get(order_id)
            if order is None:
                raise InvalidObjectId()
            response = self._planogram_order_mapper.map_to_response_model(order)
            return response
        except ValueError as ex:
            raise InvalidObjectId()
        except Exception as ex:
            raise ex
    
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