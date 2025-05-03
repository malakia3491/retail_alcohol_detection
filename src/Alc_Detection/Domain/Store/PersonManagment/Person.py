from Alc_Detection.Domain.Store.PersonManagment.Post import Post

class Person:
    def __init__(
        self,
        name: str,
        telegram_id: str,       
        is_worker=True,
        id=None,
    ):
        self.id = id
        self.name = name
        self.telegram_id = telegram_id
        self.is_worker = is_worker 

    def __eq__(self, value):
        return isinstance(value, Person) and \
               self.telegram_id == value.telegram_id
               
    def __hash__(self):
        return hash((self.name, self.telegram_id, self.is_worker))