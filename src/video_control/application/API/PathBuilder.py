from video_control.application.conf.UrlConfig import UrlConfig

class PathBuilder:
    def __init__(
        self,
        config: UrlConfig = None 
    ):        
        self._config = config if config else UrlConfig()

    @property
    def status(self) -> bool:
        return  self._config.AUTH_URL is not None and \
                self._config.RETAIL_URL is not None and \
                self._config.VIDEO_CONTROL_URL is not None and \
                self._config.BASE_URL is not None

    def get_shelvings_path(self):
        return f"{self._config.BASE_URL}{self._config.RETAIL_URL}/shelvings/"

    def login_path(self):
        return f"{self._config.BASE_URL}{self._config.AUTH_URL}/store/login/"
    
    def me_path(self):
        return f"{self._config.BASE_URL}{self._config.AUTH_URL}/store/me/"
    
    def post_video_camera_path(self, store_id: str, shelving_id: str):
        return f"{self._config.BASE_URL}{self._config.VIDEO_CONTROL_URL}/images/{store_id}/{shelving_id}"