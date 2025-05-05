from datetime import datetime

from Alc_Detection.Domain.Extentions.Utils import between

class Period:
    def __init__(
        self,
        start: datetime,
        end: datetime
    ):
        self._start = start
        self._end = end
    
    @property
    def start(self):
        return self._start
    
    @property
    def end(self):
        return self._end
    
    def between(self, date: datetime) -> bool:
        return between(date, self._start, self._end)
    
    def interception(self, period: 'Period') -> bool:
        a = period.between(self.start) or period.between(self.end)
        b = self.between(period.start) or self.between(self.end)
        return a or b
    
    def to_list(self):
        return [self._start, self._end]