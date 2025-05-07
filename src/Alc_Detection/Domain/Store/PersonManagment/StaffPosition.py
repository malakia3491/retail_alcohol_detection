from uuid import UUID

from Alc_Detection.Domain.Store.PersonManagment.Post import Post

class StaffPosition:
    def __init__(
        self,
        post: Post,
        count: int,
        id: UUID=None
    ):
        self.id = id
        self.post = post
        self.count = count 
        
    def __eq__(self, value):
        return isinstance(value, 'StaffPosition') and \
               self.post == value.post and \
               self.count == value.count
               
    def __str__(self):
        return f"StaffPosition({self.post}):, {self.count}"
               
    def __repr__(self) -> str:
        return self.__str__()               
               
    def __hash__(self):
        return hash((self.post, self.count))