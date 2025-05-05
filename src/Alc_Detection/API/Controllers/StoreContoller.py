import traceback
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Form, HTTPException, status
from fastapi.responses import JSONResponse

from Alc_Detection.Application.Requests.Models import Planogram, PlanogramOrder, PlanogramOrdersPageResponse, PlanogramOrdersResponse, ProductsResponse, ShelvingsResponse
from Alc_Detection.Application.Requests.Requests import \
(AddPermitionsRequest, AddPersonsRequest, AddPlanogramRequest, AddPostsRequest, AddProductsRequest, AddScheduleRequest, AddShelvingsRequest, AddShiftsRequest,
 AddStoresRequest, ApprovePlanogramRequest, DismissPersonRequest, UpdatePersonRequest)
from Alc_Detection.Application.StoreInformation.Services.StoreServiceFacade import StoreService

class StoreController:
    def __init__(self, 
                 store_service: StoreService):
        self.store_service = store_service
        self.router = APIRouter()
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route("/planogram_orders/",
                                  self.get_planogram_orders,
                                  methods=["GET"],
                                  status_code=status.HTTP_200_OK,
                                  response_model=PlanogramOrdersResponse)
        self.router.add_api_route("/planogram_orders/",
                                  self.add_planogram_order,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/planogram_orders/decline",
                                  self.decline_order,
                                  methods=["PUT"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/stores/",
                                  self.add_stores,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/products/",
                                  self.add_products,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/persons/",
                                  self.add_persons,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/persons/dismiss/",
                                  self.dismiss_employee,
                                  methods=["PUT"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/shelvings/",
                                  self.add_shelvings,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/planograms/",
                                  self.add_planogram,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/planograms/{order_id}/{planogram_id}/",
                                  self.get_planogram,
                                  methods=["GET"],
                                  status_code=status.HTTP_200_OK,
                                  response_model=Planogram)
        self.router.add_api_route("/planograms/approve/",
                                  self.approve_planogram,
                                  methods=["PUT"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/planograms/unapprove/",
                                  self.unapprove_planogram,
                                  methods=["PUT"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/posts/",
                                  self.add_posts,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/planogram_orders/{order_id}/",
                                  self.get_planogram_order,
                                  methods=["GET"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/planogram_orders/page/{page}",
                                  self.get_page_planogram_orders,
                                  methods=["GET"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/planogram_orders/actual/page/{page}",
                                  self.get_page_not_resolved_planogram_orders,
                                  methods=["GET"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/products/",
                                    self.get_products,
                                    methods=["GET"],
                                    status_code=status.HTTP_200_OK,
                                    response_model=ProductsResponse)
        self.router.add_api_route("/shelvings/",
                                    self.get_shelvings,
                                    methods=["GET"],
                                    status_code=status.HTTP_200_OK,
                                    response_model=ShelvingsResponse)
        self.router.add_api_route("/shelvings/{shelving_id}/",
                                  self.get_shelving,
                                  methods=["GET"],
                                  status_code=status.HTTP_200_OK,
                                  response_model=ShelvingsResponse)
        self.router.add_api_route("/schedules/",
                                  self.set_schedule,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/shifts/",
                                  self.add_shifts,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
        self.router.add_api_route("/permitions/",
                                  self.add_permitions,
                                  methods=["POST"],
                                  status_code=status.HTTP_200_OK)
    
    async def add_permitions(self, request: AddPermitionsRequest) -> dict:
        try:
            response = await self.store_service.add_permitions(request)
            return {"message": response}
        except HTTPException as he:
            raise he
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)      
    
    async def set_schedule(self, request: AddScheduleRequest) -> dict:
        try:
            response = await self.store_service.set_schedule(request)
            return {"message": response}
        except HTTPException as he:
            raise he
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def add_shifts(self, request: AddShiftsRequest) -> dict:
        try:
            response = await self.store_service.add_shifts(request)
            return {"message": response}
        except HTTPException as he:
            raise he
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def get_planogram(
        self,
        order_id: UUID,
        planogram_id: UUID
    ) -> Planogram:
        try:
            response = await self.store_service.get_planogram(
                order_id=order_id,
                planogram_id=planogram_id
            )        
            return response
        except HTTPException as he:
            raise he
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def add_planogram(self,
                            request: AddPlanogramRequest
    ) -> dict:
        try:
            await self.store_service.add_planogram(
                order_id=request.order_id,
                shelving_id=request.shelving_id,
                author_id=request.author_id,
                planogram_matrix=request.product_matrix
            )
            return {"message": "Successfully"}
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__()) 
    
    async def get_page_planogram_orders(
        self,
        page: int = 0,
        page_size: int = Form(10)
    ) -> PlanogramOrdersPageResponse:
        try:      
            response = await self.store_service.get_page_planogram_orders(
                page=page,
                page_size=page_size
            )        
            return response        
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def get_page_not_resolved_planogram_orders(
        self,
        page: int = 0,
        page_size: int = 0 
    ) -> PlanogramOrdersPageResponse:
        try:      
            response = await self.store_service.get_page_not_resolved_planogram_orders(
                page=page,
                page_size=page_size
            )        
            return response        
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def get_planogram_order(
        self,
        order_id: UUID
    ) -> PlanogramOrder:
        try:      
            response = await self.store_service.get_planogram_order(
                order_id=order_id
            )        
            return response        
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    async def get_planogram_orders(
        self,
        date_start: datetime,
        date_end: datetime
    ) -> dict:
        try:      
            response = await self.store_service.get_planogram_orders(
                date_start=date_start,
                date_end=date_end
            )        
            return response        
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
    async def add_planogram_order(
        self,
        person_id: UUID = Form(...),
        shelving_ids: list[UUID] = Form(...),
        develop_date: date = Form(...),
        implementation_date: date = Form(...),   
    ) -> dict:
        try:      
            message = await self.store_service.create_planogram_order(
                person_id=person_id,
                shelving_ids=shelving_ids,
                develop_date=develop_date,
                implementation_date=implementation_date
            )   
            return {"message": message}        
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   

    async def get_shelving(
        self,
        shelving_id: UUID
    ) -> ShelvingsResponse:
        try:      
            response = await self.store_service.get_shelving(
                shelving_id=shelving_id
            )        
            return response        
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    async def get_products(
        self
    ) -> ProductsResponse:
        try:      
            response = await self.store_service.get_products()
            return response      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def get_shelvings(
        self
    ) -> ShelvingsResponse:
        try:      
            response = await self.store_service.get_shelvings()
            return response      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    async def add_stores(
            self,
            request: AddStoresRequest
    ) -> dict:
        try:      
            message = await self.store_service.add_stores(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
    async def add_products(
            self,
            request: AddProductsRequest
    ) -> dict:
        try:      
            message = await self.store_service.add_products(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def add_persons(
            self,
            request: AddPersonsRequest
    ) -> dict:
        try:      
            message = await self.store_service.add_persons(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def add_posts(
            self,
            request: AddPostsRequest
    ) -> dict:
        try:      
            message = await self.store_service.add_posts(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def add_shelvings(
            self,
            request: AddShelvingsRequest
    ) -> dict:
        try:      
            message = await self.store_service.add_shelvings(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    async def dismiss_employee(self,
                               request: DismissPersonRequest
    ) -> dict:
        try:      
            message = await self.store_service.dismiss_employee(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    async def approve_planogram(self, 
                                request: ApprovePlanogramRequest
    ) -> dict:
        try:      
            message = await self.store_service.approve_planogram(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    async def unapprove_planogram(self, 
                                  request: ApprovePlanogramRequest
    ) -> dict:
        try:      
            message = await self.store_service.unapprove_planogram(request)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    async def decline_order(self,
                            person_id: UUID = Form(...), 
                            order_id: UUID = Form(...),
                                  
    ) -> dict:
        try:      
            message = await self.store_service.decline_planogram_order(person_id=person_id,
                                                                      order_id=order_id)
            return {"message": message}      
        except HTTPException as he:
            raise he        
        except Exception as e:
            return JSONResponse(
                content={"message": f"Internal error: {str(e)}"},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)