from pathlib import Path

from .application.API.ApiRequester import ApiRequester
from .application.API.PathBuilder import PathBuilder
from .application.services.ShelvingService import ShelvingService
from .application.services.AuthService import AuthService
from .application.services.ConfigEditor import ConfigEditor
from .application.videocamers.CameraService import CameraService
from .application.videocamers.StreamService import StreamService
from .persistance.repositories.ShelvingRepository import ShelvingRepository
from .persistance.cache.InMemoryCache import InMemoryCache
from .persistance.repositories.VideocameraRepository import VideocameraRepository
from .persistance.store.JsonStore import JsonStore

HERE = Path(__file__).resolve().parent          
PERSISTENCE = HERE / "persistance" / "data"     
CONF_INI = PERSISTENCE / "conf.ini"
CAMERAS_JSON = PERSISTENCE / "cameras.json"

class Inicializator:
    def __init__(self, pathes: dict[str, str] = None):
        self._pather = pathes
        self._config_reader = ConfigEditor(str(CONF_INI))

    async def initialize(self):
        config = self._config_reader.load_config()
        url_config = self._config_reader.load_url_config()
        
        path_builder = PathBuilder(config=url_config)     
        requester = ApiRequester(path_builder=path_builder)     
        json_store = JsonStore(filepath=str(CAMERAS_JSON))
        camera_repository = await VideocameraRepository(
            json_store=json_store,
            cache=InMemoryCache(),
        ).on_start()
        shelving_repository = ShelvingRepository(
            cache=InMemoryCache()
        )
        auth_service = await AuthService(
            requester=requester,
            config=config
        ).on_start()
        camera_service = await CameraService(
            camera_repository=camera_repository,
        ).on_start()
        shelving_service = await ShelvingService(
            requester=requester,
            shelving_repository=shelving_repository
        ).on_start()
        stream_service = StreamService(
            auth_service=auth_service,            
            camera_service=camera_service,
            shelving_service=shelving_service,
            camera_repository=camera_repository,
            requester=requester,
            jpeg_quality=80 
        )
        return auth_service, camera_service, shelving_service, stream_service, self._config_reader      