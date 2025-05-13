from Alc_Detection.Domain.RetailModel import RetailModel


class Shelving(RetailModel):
    def __init__(self, name, shelves_count, retail_id=None, id=None):
        super().__init__(retail_id=retail_id)
        self.id = id
        self.name = name
        self.shelves_count = shelves_count
        
    def __eq__(self, value):
        return isinstance(value, Shelving) and \
               self.name == value.name and \
               self.shelves_count == value.shelves_count \
    
    def __hash__(self):
        return hash((self.name, self.shelves_count))