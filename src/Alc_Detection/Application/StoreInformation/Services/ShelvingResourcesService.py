
import traceback
from fastapi import HTTPException, status
from Alc_Detection.Application.Requests.Responses import ShelvingsResponse
from Alc_Detection.Domain.Entities import *
from Alc_Detection.Application.StoreInformation.Exceptions.Exceptions import (
     InvalidObjectId,
)
from Alc_Detection.Application.Requests.Requests import (
    AddShelvingsRequest, Shelving as ShelvingModel)

from Alc_Detection.Persistance.Repositories.Repositories import *

class ShelvingResourcesService:
    def __init__(self, shelving_repository: ShelvingRepository):
        self._shelving_repository = shelving_repository
    
    async def get_shelving(
        self,
        shelving_id: str
    ) -> ShelvingsResponse:
        try:
            shelving = await self._shelving_repository.get(shelving_id)
            if shelving is None:
                raise InvalidObjectId()
            response = ShelvingsResponse(
                shelvings=[ShelvingModel(
                    id=shelving.id,
                    shelves_count=shelving.shelves_count,
                    name=shelving.name)]
            )
            return response
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())
            
    async def get_shelvings(self) -> ShelvingsResponse:
        try:
            shelvings = await self._shelving_repository.get_all()
            response = ShelvingsResponse(
                shelvings=[ShelvingModel(
                    id=shelving.id,
                    shelves_count=shelving.shelves_count,
                    name=shelving.name)
                           for shelving in shelvings])
            return response
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
            
    async def load_shelvings(self, shelvings: list[Shelving]) -> str:
        try:
            count_added_records = await self._shelving_repository.add(*shelvings)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())