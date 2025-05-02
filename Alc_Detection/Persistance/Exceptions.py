from typing import Type

class ObjectNotFound(Exception):
    """Exception raised when an object is not found in the database."""
    def __init__(self, object_type: Type, object_id: str):
        self.object_type = object_type.__name__
        self.object_id = object_id
        
    def __str__(self):
        return f"{self.object_type} with ID {self.object_id} not found in the database."
        
class ObjectUpdateException(Exception):
    def __init__(self, object_type: Type, object_id: str):
        self.object_type = object_type.__name__
        self.object_id = object_id
        
    def __str__(self):
        return f"{self.object_type} with ID {self.object_id} not update in the database."