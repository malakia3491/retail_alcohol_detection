from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Store.Shelving import Shelving

class Message:
    def __init__(
        self,
        user_ids: list[str],
        realogram_img_src: str,
        planogram_img_src: str,
        incident: Incident,
    ):
        self._user_ids = user_ids
        self._realogram_img_src = realogram_img_src
        self._planogram_img_src = planogram_img_src
        self._incident = incident
        
    def build(self) -> str:
        return self._incident.build_message_text() 
    
    @property
    def planogram_img(self) -> tuple[str, str]:
        return ("Планограмма", self._planogram_img_src)
    
    @property
    def realogram_img(self) -> tuple[str, str]:
        return ("Реалограмма", self.realogram_img_src)
    
    @property
    def user_ids(self):
        return self._user_ids