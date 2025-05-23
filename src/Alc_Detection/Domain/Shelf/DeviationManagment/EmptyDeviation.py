from datetime import time

from Alc_Detection.Domain.Store.PersonManagment.Person import Person
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation

class EmptyDeviation(Deviation):
    def __init__(
        self,
        product_box: ProductBox,
        responsible_employees: list[Person]=[],
        elimination_time: time=None,
    ):
        super().__init__(
            product_box=product_box,
            elimination_time=elimination_time,
            responsible_employees=responsible_employees
        )
        self._is_enough_product=True    
    
    @property
    def is_enough_product(self):
        return self._is_enough_product
    
    @is_enough_product.setter
    def is_enough_product(self, value: bool):
        self._is_enough_product = value

    def add_responsible_employees(self, person: Person):
        super().add_responsible_employees(person)
        
    def __eq__(self, value):
        return isinstance(value, EmptyDeviation) and \
               self.position == value.position
               
    def __str__(self):
        return f"{self.product}"