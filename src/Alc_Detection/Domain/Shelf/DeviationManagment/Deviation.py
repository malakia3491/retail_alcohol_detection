from datetime import time

from Alc_Detection.Domain.Shelf.ProductMatrix.Point import Point
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Store.PersonManagment.Person import Person

class Deviation:
    def __init__(
        self,
        product_box: ProductBox,
        responsible_employees: list[Person]=[],
        elimination_time: time=None,
    ):
        self._product_box = product_box
        self._elimination_time = elimination_time
        self._responsible_employees = responsible_employees
        self._send_time = None
        self._realogram = None
        
    @property
    def product(self):
        return self._product_box.product
    
    @property
    def product_box(self):
        return self._product_box
    
    @property 
    def position(self) -> Point:
        return self._product_box.position
    
    @property
    def send_time(self):
        return self._send_time
    
    @send_time.setter
    def send_time(self, time: time):
        self._send_time = time
    
    @property
    def elimination_time(self):
        return self._elimination_time
    
    @elimination_time.setter
    def elimination_time(self, value: time):
        if value < self.send_time:
            raise ValueError(value)
        self._elimination_time = value
    
    @property
    def reaction_time(self):
        if self._elimination_time == None:
            return None
        return self._elimination_time - self._send_time
    
    @property
    def is_resolved(self):
        return not self.reaction_time is None 
    
    @property
    def realogram(self):
        return self._realogram
    
    @realogram.setter
    def realogram(self, value):
        self._realogram = value
    
    @property
    def shelving(self):
        return self._realogram.planogram.shelving
    
    @property
    def responsible_employees(self):
        return self._responsible_employees
    
    def add_responsible_employees(self, person: Person):
        if not person in self._responsible_employees:
            self._responsible_employees.append(person)
            
    def __eq__(self, value):
        return isinstance(value, Deviation) and \
               self.position == value.position
               
    def __hash__(self):
        return hash(self.position)
               