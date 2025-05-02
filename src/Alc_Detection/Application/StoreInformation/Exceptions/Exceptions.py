from typing import Type
from fastapi import HTTPException, status

class PlanogramOrderIsNotResolved(HTTPException):
    def __init__(self, order_id, order_create_date):
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"Планограмма из приказа на создание и разработку планограмм с номером {order_id} от {order_create_date} не была одобрена или добавлена!")

class ShelvingPlanogramIsAgreed(HTTPException):
    def __init__(self, order_id, order_create_date, shelving_name):
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"В рамках приказа с номером {order_id} от {order_create_date} планограмма для стеллажа {shelving_name} уже была одобрена!")
        
class ShelvingIsNotAssigned(HTTPException):
    def __init__(self, order_id, order_create_date, shelving_name):
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            f"В рамках приказа с номером {order_id} от {order_create_date} планограмма для стеллажа {shelving_name} не разрабатывается!")   
        
class IncorrectPlanogram(HTTPException):
    def __init__(self, shelving_name: str, shelving_shelves_count: int, shelfs_len: int):
        super().__init__(
           status.HTTP_400_BAD_REQUEST,
           f"Shelving {shelving_name} has {shelving_shelves_count} shelves, but planogram has {shelfs_len} shelves.")
 
class IncorrectUpdateData(HTTPException):
    def __init__(self, object_type: Type, field_names: list[str]):
        super().__init__(  
            status.HTTP_400_BAD_REQUEST,
            f"For update {object_type.__name__} need fields: {', '.join(field_names)}")
        
class PersonIsNotWorkerAlready(HTTPException):
    def __init__(self, name: str):
        super().__init__(  
            status.HTTP_400_BAD_REQUEST,
            f"Person {name} is not worker already")
        
class InvalidObjectId(HTTPException):
    def __init__(self):
        super().__init__(  
            status.HTTP_400_BAD_REQUEST,
            f"Some object was not found")
                
class CalibrationException(HTTPException):
    def __init__(self, planogram_id: str):
        super().__init__(  
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"Invalid calibration boxes for planogram {planogram_id}")
                
class InvalidPlanogramApprove(HTTPException):
    def __init__(self, planogram_id: str):
        super().__init__(  
            status.HTTP_400_BAD_REQUEST,
            f"Invalid approve planogram with id {planogram_id}")
        
class InvalidPlanogramUnapprove(HTTPException):
    def __init__(self, planogram_id: str):
        super().__init__(  
            status.HTTP_400_BAD_REQUEST,
            f"Invalid unapprove planogram with id {planogram_id}")
        