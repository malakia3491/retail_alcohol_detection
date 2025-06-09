from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed

class Person(IndexNotifiable):
    def __init__(
        self,
        name: str,
        email: str,
        retail_id: str=None,
        telegram_id: str=None,
        password_hash: str=None,      
        is_store_worker=True,
        is_active=True,
        id=None,
    ):
        super().__init__()
        self._id = id
        self._retail_id = retail_id
        self._name = name
        self._email = email
        self._telegram_id = telegram_id
        self.is_store_worker = is_store_worker
        self.is_active = is_active
        self.password_hash = password_hash 

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name

    @indexed
    @property
    def retail_id(self) -> str:
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)     

    @indexed
    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email):
        old = self._email
        self._email = new_email
        self._notify_index_changed('email', old, new_email)
        
    @indexed
    @property
    def telegram_id(self):
        return self._telegram_id

    @telegram_id.setter
    def telegram_id(self, value):
        old = self._telegram_id
        self._telegram_id = value
        self._notify_index_changed('telegram_id', old, value)    

    def __eq__(self, value):
        return isinstance(value, Person) and \
               self.email == value.email
               
    def __hash__(self):
        return hash(self.email)