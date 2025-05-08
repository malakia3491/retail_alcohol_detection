from typing import List, Optional
from datetime import datetime
from uuid import UUID

from Alc_Detection.Application.IncidentManagement.Settings import Settings
from Alc_Detection.Application.Mappers.ScheduleMapper import ScheduleMapper
from Alc_Detection.Application.Mappers.ShiftMapper import ShiftMapper
from Alc_Detection.Application.Mappers.StoreMapper import StoreMapper
from Alc_Detection.Application.StoreInformation.Services.RealogramResourcesService import RealogramResourcesService
from Alc_Detection.Application.StoreInformation.Services.PersonManagementService import PersonManagementService
from Alc_Detection.Application.StoreInformation.Services.PlanogramOrderResourcesService import PlanogramOrderResourcesService
from Alc_Detection.Application.StoreInformation.Services.PlanogramResourcesService import PlanogramResourcesService
from Alc_Detection.Application.StoreInformation.Services.ProductResourcesService import ProductResourcesService
from Alc_Detection.Application.StoreInformation.Services.ShelvingResourcesService import ShelvingResourcesService

from Alc_Detection.Application.StoreInformation.Services.StoreResourcesService import StoreResourcesService
from Alc_Detection.Domain.Shelf.Planogram import Planogram
from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Domain.Store.Product import Product
from Alc_Detection.Persistance.Repositories.PermitionRepository import PermitionRepository
from Alc_Detection.Persistance.Repositories.Repositories import (
    StoreRepository,
    PersonRepository,
    ShelvingRepository,
    PostRepository,
    PlanogramOrderRepository,
    ProductRepository
)
from Alc_Detection.Application.Mappers.PlanogramOrderMapper import PlanogramOrderMapper
from Alc_Detection.Application.Mappers.PlanogramMapper import PlanogramMapper
from Alc_Detection.Application.Mappers.ProductMatrixMapper import ProductMatrixMapper
from Alc_Detection.Application.ImageGeneration.ProductMatrixImageGenerator import ProductMatrixImageGenerator
from Alc_Detection.Application.Requests.Requests import (
    AddPermitionsRequest,
    AddPersonsRequest,
    AddPostsRequest,
    AddScheduleRequest,
    AddShiftAssignment,
    DismissPersonRequest,
    AddShelvingsRequest,
    AddProductsRequest,
    ApprovePlanogramRequest,
    AddShiftsRequest,
    AddProductsRequest as AddProductsRequestModel
)
from Alc_Detection.Application.Requests.Models import (
    PlanogramComplianceReport,
    PlanogramUsageReport,
    PlanogramsResponse,
    RealogramsResponse,
    ShelvingsResponse,
    ProductsResponse,
    PlanogramOrdersPageResponse,
    PlanogramOrdersResponse,
    ProductMatrix as ProductMatrixModel,
    PlanogramOrdersResponse as OrdersResponseModel,
    StoresResponse
)

class StoreService:
    def __init__(
        self,
        store_mapper: StoreMapper,
        store_repository: StoreRepository,
        person_repository: PersonRepository,
        post_repository: PostRepository,
        shelving_repository: ShelvingRepository,
        planogram_order_repository: PlanogramOrderRepository,
        product_repository: ProductRepository,
        permition_repository: PermitionRepository,
        image_generator: ProductMatrixImageGenerator,
        shift_mapper: ShiftMapper,
        schedule_mapper: ScheduleMapper,
        planogram_order_mapper: PlanogramOrderMapper,
        planogram_mapper: PlanogramMapper,
        product_matrix_mapper: ProductMatrixMapper,
        settings: Settings,
    ) -> None:
        # Initialize underlying services
        
        self.store_service = StoreResourcesService(
            store_mapper=store_mapper,
            store_repository=store_repository,
            settings=settings
        )
        self.realogram_service = RealogramResourcesService(
            store_repository=store_repository,
            shelving_repository=shelving_repository,
            planogram_order_repository=planogram_order_repository,
            person_repository=person_repository,
            product_repository=product_repository,
            planogram_order_mapper=planogram_order_mapper,
            planogram_mapper=planogram_mapper,
            product_matrix_mapper=product_matrix_mapper
        )
        
        self.person_service = PersonManagementService(
            store_repository=store_repository,
            person_repository=person_repository,
            post_repository=post_repository,
            shift_mapper=shift_mapper,
            schedule_mapper=schedule_mapper,
            permition_repository=permition_repository
        )
        self.shelving_service = ShelvingResourcesService(
            shelving_repository=shelving_repository
        )
        self.planogram_order_service = PlanogramOrderResourcesService(
            shelving_repository=shelving_repository,
            planogram_order_repository=planogram_order_repository,
            person_repository=person_repository,
            planogram_order_mapper=planogram_order_mapper
        )
        self.planogram_service = PlanogramResourcesService(
            image_generator=image_generator,
            store_repository=store_repository,
            shelving_repository=shelving_repository,
            planogram_order_repository=planogram_order_repository,
            person_repository=person_repository,
            product_repository=product_repository,
            planogram_order_mapper=planogram_order_mapper,
            planogram_mapper=planogram_mapper,
            product_matrix_mapper=product_matrix_mapper
        )
        self.product_service = ProductResourcesService(
            product_repository=product_repository
        )

    async def get_planogram_usage_report(self, start: datetime, end: datetime) -> PlanogramUsageReport:
        return await self.store_service.generate_planogram_usage_report(start, end)

    async def get_planogram_compliance_report(self, start: datetime, end: datetime) -> PlanogramComplianceReport:
        return await self.store_service.generate_planogram_compliance_report(start, end)

    async def add_shift_assignment(self, request: AddShiftAssignment) -> str:
        return await self.person_service.add_shift_assignment(request)

    async def get_stores(self) -> StoresResponse:
        return await self.store_service.get_stores()
    
    async def get_actual_realograms(self, store_id: UUID) -> RealogramsResponse:
        return await self.realogram_service.get_actual_realograms(store_id)
    
    # Person management facade methods
    async def add_persons(self, request: AddPersonsRequest) -> str:
        return await self.person_service.add_persons(request)

    async def dismiss_employee(self, request: DismissPersonRequest) -> str:
        return await self.person_service.dismiss_employee(request)

    async def get_work_place(self, person_id: UUID) -> Optional[tuple[Store, Shift, Post]]:
        return await self.person_service.get_work_place(person_id)

    async def set_schedule(self, request: AddScheduleRequest) -> str:
        return await self.person_service.set_schedule(request)

    async def add_shifts(self, request: AddShiftsRequest) -> str:
        return await self.person_service.add_shifts(request)

    async def add_posts(self, request: AddPostsRequest) -> str:
        return await self.person_service.add_posts(request)

    async def add_permitions(self, request: AddPermitionsRequest) -> str:
        return await self.person_service.add_permitions(request)

    # Shelving management
    async def get_shelvings(self) -> ShelvingsResponse:
        return await self.shelving_service.get_shelvings()

    async def add_shelvings(self, request: AddShelvingsRequest) -> str:
        return await self.shelving_service.add_shelvings(request)

    async def get_shelving(self, shelving_id: UUID) -> ShelvingsResponse:
        return await self.shelving_service.get_shelving(shelving_id)

    # Product management
    async def get_products(self) -> ProductsResponse:
        return await self.product_service.get_products()

    async def add_products(self, request: AddProductsRequestModel) -> str:
        return await self.product_service.add_products(request)

    async def get_actual_product_count(
        self,
        store: Store,
        product: Product
    ) -> int:
        return await self.product_service.get_actual_product_count(store=store, product=product)

    # Planogram orders
    async def get_page_not_resolved_planogram_orders(
        self, page: int, page_size: int
    ) -> PlanogramOrdersPageResponse:
        return await self.planogram_order_service.get_page_not_resolved_planogram_orders(page, page_size)

    async def get_page_planogram_orders(
        self, page: int, page_size: int
    ) -> PlanogramOrdersPageResponse:
        return await self.planogram_order_service.get_page_planogram_orders(page, page_size)

    async def get_planogram_order(self, order_id: UUID) -> OrdersResponseModel:
        return await self.planogram_order_service.get_planogram_order(order_id)

    async def create_planogram_order(
        self,
        person_id: UUID,
        shelving_ids: List[str],
        develop_date: datetime,
        implementation_date: datetime
    ) -> str:
        return await self.planogram_order_service.create_planogram_order(
            person_id, shelving_ids, develop_date, implementation_date
        )

    async def decline_planogram_order(self, person_id: UUID, order_id: UUID) -> str:
        return await self.planogram_order_service.decline_planogram_order(person_id, order_id)

    # Planogram operations
    async def get_last_agreed_planograms(self) -> PlanogramsResponse:
        return await self.planogram_service.get_last_agreed_planograms()
    
    async def get_planogram(self, order_id: UUID, planogram_id: UUID) -> OrdersResponseModel:
        return await self.planogram_service.get_planogram(order_id, planogram_id)

    async def add_planogram(
        self,
        order_id: UUID,
        shelving_id: UUID,
        author_id: UUID,
        planogram_matrix: ProductMatrixModel
    ) -> None:
        return await self.planogram_service.add_planogram(order_id, shelving_id, author_id, planogram_matrix)

    async def approve_planogram(self, request: ApprovePlanogramRequest) -> str:
        return await self.planogram_service.approve_planogram(request)

    async def unapprove_planogram(self, request: ApprovePlanogramRequest) -> str:
        return await self.planogram_service.unapprove_planogram(request)

    async def get_calibrated_planogram(self, store_id: UUID, shelving_id: UUID) -> Planogram:
        return await self.planogram_service.get_calibrated_planogram(store_id, shelving_id)

    async def calibrate_store_planogram(
        self,
        person_id: UUID,
        store_id: UUID,
        order_id: UUID,
        shelving_id: UUID,
        calibration_boxes: List
    ) -> str:
        return await self.planogram_service.calibrate_store_planogram(person_id, store_id, order_id, shelving_id, calibration_boxes)

    async def get_last_agreed_planograms(self) -> dict:
        return await self.planogram_service.get_last_agreed_planograms()

    # Additional convenience methods can be added below
