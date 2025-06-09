from video_control.domain.Shelving import Shelving
from video_control.application.API.ApiRequester import ApiRequester
from video_control.persistance.repositories.ShelvingRepository import ShelvingRepository

class ShelvingService:
    def __init__(
        self,
        requester: ApiRequester,
        shelving_repository: ShelvingRepository
    ):
        self._requester = requester
        self._shelving_repository = shelving_repository
    
    async def on_start(self) -> 'ShelvingService':
        """
        Initialize the camera service.
        This method can be used to perform any necessary setup when the service starts.
        """
        shelvings: list[Shelving] = []
        if not self._shelving_repository.is_filled and self._requester.ready:
            data = await self._requester.get_shelvings()
            for shelving_obj in data:
                shelving = Shelving(
                    id=shelving_obj.get("id"),
                    name=shelving_obj.get("name"),
                )
                shelvings.append(shelving)
            await self._shelving_repository.on_start(items=shelvings)
        print(f'ShelvingService: initialized {shelvings}')
        return self
                
    async def load(self) -> None:
        if self._requester.ready:
            data = await self._requester.get_shelvings()
            for shelving_obj in data:
                shelving = Shelving(
                    id=shelving_obj.get("id"),
                    name=shelving_obj.get("name"),
                )
                await self._shelving_repository.add(shelving)
                
    async def get_shelvings(self) -> list[Shelving]:
        """
        Retrieve all shelvings from the repository.
        
        :return: List of Shelving objects.
        """
        return await self._shelving_repository.get_all()