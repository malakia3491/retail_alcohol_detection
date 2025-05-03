from Alc_Detection.Domain.Store.PersonManagment.Post import Post
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift

class StaffPosition:
    def __init__(
        self,
        post: Post,
        shift: Shift,
        id: str=None
    ):
        self.id = id
        self._post = post
        self._shift = shift
        
    @property
    def shift(self):
        return self._shift
    
    @property
    def post(self):
        return self._post