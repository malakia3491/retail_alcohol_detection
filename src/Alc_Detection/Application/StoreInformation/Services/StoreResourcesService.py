from Alc_Detection.Application.Mappers.StoreMapper import StoreMapper
from Alc_Detection.Application.Requests.Models import StoresResponse
from Alc_Detection.Persistance.Repositories.StoreRepository import StoreRepository

class StoreResourcesService:
    def __init__(
        self,
        store_repository: StoreRepository,
        store_mapper: StoreMapper
    ):
        self._store_repository = store_repository
        self._store_mapper = store_mapper
        
    async def get_stores(self) -> StoresResponse:
        stores = await self._store_repository.get_all_not_office()
        return StoresResponse(
            stores=[self._store_mapper.map_to_response_model(store) for store in stores ]
        )