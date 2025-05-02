from datetime import time

from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation
from Alc_Detection.Domain.Shelf.DeviationManagment.EmptyDeviation import EmptyDeviation
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Store.Person import Person

class Incident:
    def __init__(self,
                 send_time: time,
                 realogram: Realogram,
                 deviations: list[Deviation],
                 responsible_employees: list[Person],
                 shift=None,
                 id=None,
    ):
        self.id = id 
        self._send_time = send_time
        self._realogram = realogram
        self._shift = shift
        self._responsible_employees = responsible_employees
        self._add_deviations(deviations)
    
    def build_message_text(self):
        shelfs_strs: dict[int, str] = {}
        for deviation in self.deviations:
            if deviation.position.x in shelfs_strs:
                shelfs_strs[deviation.position.x] += f"{deviation }"
            else:    
                shelfs_strs[deviation.position.x] = f"{deviation }"        
        result = f"Время обнаружения {self.realogram.create_date.time()}\n"+\
                 f"Стеллаж: {self.realogram.shelving.name}"+\
                 f"{self._define_title()}\n"
        for id, string in shelfs_strs:                            
            result += f"Полка {id+1}: " + string + "\n"                
            
        return result
                            
    def _define_title(self):
        if isinstance(self.deviations[0], EmptyDeviation):
            return "На стеллаже нет товаров:"
        return "Товары на стеллаже не соответствуют планограмме:"
    
    def _add_deviations(self, deviations: list[Deviation]):
        self._deviations = deviations
        for deviation in deviations:
            deviation.send_time = self.send_time
            deviation.realogram = self.realogram 
    
    @property
    def send_time(self):
        return self._send_time
    
    @property
    def elimination_time(self):
        deviations = sorted(
            self._deviations,
            key=lambda d: d.elimination_time,
            reverse=True
        )        
        return deviations[0].elimination_time
    
    @property
    def reaction_time(self): 
        return self.elimination_time - self._send_time
    
    @property
    def is_resolved(self):
        return not self.elimination_time is None 
    
    @property
    def realogram(self):
        return self._realogram
    
    @property
    def shelving(self):
        return self.realogram.planogram.shelving
    
    @property
    def responsible_employees(self):
        return self._responsible_employees
    
    @property
    def deviation_count(self):
        return len(self._deviations)
    
    @property 
    def deviations(self):
        return self._deviations
    
    def resolve(self, time: time):
        if time < self.send_time:
            raise ValueError(time)
        for deviation in self._deviations:
            deviation.elimination_time = time
        
    def contains(self, *deviations: Deviation):
        return all(self._contains(deviation) for deviation in deviations)
    
    def _contains(self, deviation: Deviation):
        return deviation in self.deviations