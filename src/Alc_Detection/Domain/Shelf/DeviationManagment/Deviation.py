from datetime import time

from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Store.Person import Person

class Deviation:
    def __init__(
        self,
        product_box: ProductBox,
        responsible_employees: list[Person],
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
    
    @realogram.__setter_
    def realogram(self, value: Realogram):
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