class UrlConfig:
    def __init__(
        self,
        base_url: str=None,
        retail_url: str=None,
        video_contorl_url: str=None,
        auth_url: str=None
    ):
        """
        Initializes the URL configuration for the video control application.
        This class defines various endpoints used in the application.
        """
        self._base_url = base_url
        self._retail_url = retail_url
        self._video_contorl_url = video_contorl_url
        self._auth_url = auth_url

    def from_dict(self, **args):
        """
        Create a Confing instance from a dictionary.
        
        :param args: Dictionary containing configuration parameters.
        :return: Confing instance.
        """
        return UrlConfig(
            base_url=args.get('BASE_URL', ''),
            retail_url=args.get('RETAIL_URL', ''),
            video_contorl_url=args.get('VIDEO_CONTROL_URL', ''),
            auth_url=args.get('AUTH_URL', '')
        )
        
    @property
    def BASE_URL(self):
        return self._base_url
    
    @property
    def RETAIL_URL(self):
        return self._retail_url
    
    @property
    def VIDEO_CONTROL_URL(self):
        return self._video_contorl_url
    
    @property
    def AUTH_URL(self):
        return self._auth_url