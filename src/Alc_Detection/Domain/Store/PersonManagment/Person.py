class Person:
    def __init__(
        self,
        name: str,
        email: str,
        telegram_id: str=None,
        password_hash: str = None,      
        is_store_worker=True,
        is_active=True,
        id=None,
    ):
        self.id = id
        self.name = name
        self.email = email
        self.telegram_id = telegram_id
        self.is_store_worker = is_store_worker
        self.is_active = is_active
        self.password_hash = password_hash 

    def __eq__(self, value):
        return isinstance(value, Person) and \
               self.email == value.email
               
    def __hash__(self):
        return hash(self.email)