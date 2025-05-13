from datetime import datetime

from Alc_Detection.Domain.Date.extensions import Period
from Alc_Detection.Domain.RetailModel import RetailModel

class Schedule(RetailModel):
    def __init__(
        self,
        date_assignment: datetime,
        holidays: list[datetime],
        date_from: datetime,
        date_to: datetime,
        retail_id: str=None,
        id: str=None
    ):
        super().__init__(retail_id=retail_id)
        self.id = id
        self._date_assignment = date_assignment
        self._holidayes = holidays
        self._period = Period(start=date_from,
                              end=date_to)

    @property
    def days(self):
        return self._holidayes
    
    @property
    def period(self):
        return self._period
    
    @property
    def date_assignment(self):
        return self._date_assignment                

    def is_conflict(self, schedule: 'Schedule'):
        return self._period.interception(schedule.period)

    def between(self, date: datetime):
        return self._period.between(date)

    def contains(self, date: datetime):
        return date in self._holidayes