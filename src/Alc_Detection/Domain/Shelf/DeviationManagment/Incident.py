from datetime import datetime, time

from Alc_Detection.Domain.Shelf.DeviationManagment.Deviation import Deviation
from Alc_Detection.Domain.Shelf.DeviationManagment.EmptyDeviation import EmptyDeviation
from Alc_Detection.Domain.Shelf.ProductMatrix.ProductBox import ProductBox
from Alc_Detection.Domain.Shelf.Realogram import Realogram
from Alc_Detection.Domain.Store.PersonManagment.Person import Person

class Incident:
    def __init__(self,
                 send_time: time,
                 realogram: Realogram,
                 deviations: list[Deviation],
                 responsible_employees: list[Person],
                 id=None,
    ):
        self.id = id 
        self._send_time = send_time
        self._realogram = realogram
        self._responsible_employees = responsible_employees
        self._add_deviations(deviations)
    
    def build_message_text(self):
        shelfs_strs: dict[int, str] = {}
        for deviation in self.deviations:
            if deviation.position.x in shelfs_strs:
                shelfs_strs[deviation.position.x] += f"{deviation} "
            else:    
                shelfs_strs[deviation.position.x] = f"{deviation} "        
        time = f"{self.realogram.create_date.hour}:{self.realogram.create_date.minute}:{self.realogram.create_date.second}"
        result = f"<b>Время обнаружения:</b> {time}\n"+\
                 f"<b>Стеллаж:</b> {self.realogram.shelving.name}\n\n"+\
                 f"{self._define_title()}\n"
        for id, string in shelfs_strs.items():                            
            result += f"Полка {id+1}: \n" + string + "\n"                
            
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
    def type(self) -> str:
        if isinstance(self.deviations[0], EmptyDeviation):
            if not self.deviations[0].is_enough_product:
                return "Нет товаров"
            else: return "Пустоты"
        else: return "Несоблюдения планограммы"
            
    @property
    def send_time(self) -> datetime:
        return self._send_time
    
    @property
    def elimination_time(self) -> datetime:
        is_resolved = True
        for deviation in self.deviations:
            if deviation.elimination_time is None:
                is_resolved = False
                return None
        
        if self.deviations and is_resolved:
            deviations = sorted(
                self._deviations,
                key=lambda d: d.elimination_time,
                reverse=True
            )        
            return deviations[0].elimination_time
        return None
    
    @property
    def reaction_time(self) -> float: 
        seconds_diff = None
        if self.elimination_time and self.send_time:
            delta = self.elimination_time - self.send_time
            seconds_diff = delta.total_seconds()
        return seconds_diff
    
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
    def not_resolved_deviations(self) -> list[Deviation]:
        not_resolved_deviations = []
        for deviation in self._deviations:
            if not deviation.is_resolved:
                not_resolved_deviations.append(deviation)
        return not_resolved_deviations
    
    @property 
    def deviations(self):
        return self._deviations
    
    def resolve(self, time: time):
        if time < self.send_time:
            raise ValueError(time)
        for deviation in self._deviations:
            deviation.elimination_time = time
        
    def contains(self, deviation: Deviation):
        for dev in self.not_resolved_deviations:
            if dev.position == deviation.position:
                return True
        return False 
    
    def __str__(self):
        return f"{self.deviation_count} {self.send_time} {self.deviations}"
    
    def __repr__(self) -> str:
        return self.__str__()    