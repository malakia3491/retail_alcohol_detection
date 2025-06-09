from Alc_Detection.Domain.IndexNotifiable import IndexNotifiable, indexed

class Shelving(IndexNotifiable):
    def __init__(self, name, shelves_count, retail_id=None, id=None):
        super().__init__()
        self.id = id
        self._retail_id = retail_id
        self.name = name
        self.shelves_count = shelves_count
    
    @indexed       
    @property
    def retail_id(self):
        return self._retail_id
    
    @retail_id.setter
    def retail_id(self, value: str):
        old = self._retail_id
        self._retail_id = value
        self._notify_index_changed('retail_id', old, value)   
        
    def __eq__(self, value):
        return isinstance(value, Shelving) and \
               self.name == value.name and \
               self.shelves_count == value.shelves_count \
    
    def __hash__(self):
        return hash((self.name, self.shelves_count))