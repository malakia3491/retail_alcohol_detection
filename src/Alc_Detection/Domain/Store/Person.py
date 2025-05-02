class Person:
    def __init__(self, name, telegram_id, post=None, id=None, store=None, is_worker=True):
        self.id = id
        self.store = store
        self.name = name
        self.post = post
        self.telegram_id = telegram_id
        self.is_worker = is_worker 

    def __eq__(self, value):
        return isinstance(value, Person) and \
               self.telegram_id == value.telegram_id
    def __hash__(self):
        return hash((self.name, self.telegram_id, self.is_worker, self.store))