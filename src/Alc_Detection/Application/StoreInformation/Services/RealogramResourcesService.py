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
     InvalidObjectId, InvalidPlanogramApprove, InvalidPlanogramUnapprove,
    ShelvingIsNotAssigned,
     ShelvingPlanogramIsAgreed
)
from Alc_Detection.Application.Requests.Requests import (
    ApprovePlanogramRequest,
    ProductMatrix as ProductMatrixModel)
from Alc_Detection.Application.Requests.Models import (
    Planogram as PlanogramModel,
    PlanogramDataResponse,
    PlanogramsResponse,
    Realogram as RealogramApiModel,
    RealogramsResponse
)
from Alc_Detection.Application.Mappers.PlanogramOrderMapper import PlanogramOrderMapper
from Alc_Detection.Application.Mappers.ProductMatrixMapper import ProductMatrixMapper
from Alc_Detection.Persistance.Repositories.Repositories import *

class RealogramResourcesService:
    def __init__(self,
                 store_repository: StoreRepository,
                 shelving_repository: ShelvingRepository,
                 planogram_order_repository: PlanogramOrderRepository,
                 person_repository: PersonRepository,
                 product_repository: ProductRepository,
                 planogram_order_mapper: PlanogramOrderMapper,
                 planogram_mapper: PlanogramMapper,
                 product_matrix_mapper: ProductMatrixMapper,):
        self._planogram_mapper = planogram_mapper
        self._store_repository = store_repository
        self._shelving_repository = shelving_repository
        self._planogram_order_repository = planogram_order_repository
        self._person_repository = person_repository
        self._product_repository = product_repository
        self._product_matrix_mapper = product_matrix_mapper
        self._planogram_order_mapper = planogram_order_mapper
        
    async def get_actual_realograms(
        self,
        store_id: str
    ) -> RealogramsResponse:     
        store = await self._store_repository.get(store_id)
        shelvings = await self._shelving_repository.get_all()
        actual_realograms = store.get_actual_realograms(shelvings)
        realograms: list[RealogramApiModel] = []
        for shelving, realogram in actual_realograms.items():
            realogram_response = RealogramApiModel(
                id=realogram.id,
                planogram_id=realogram.planogram.id,
                shelving_id=shelving.id,
                img_src=realogram.image_url,
                create_date=realogram.create_date,
                product_matrix=self._product_matrix_mapper.map_to_response_model(realogram.product_matrix, realogram.planogram.product_count),
                accordance=realogram.accordance,
                empties_count=realogram.empty_count
            )
            realograms.append(realogram_response)
        return RealogramsResponse(
            realograms=realograms
        )