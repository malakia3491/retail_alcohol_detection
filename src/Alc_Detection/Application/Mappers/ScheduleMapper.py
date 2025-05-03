from datetime import datetime
from Alc_Detection.Domain.Store.PersonManagment.Schedule import Schedule
from Alc_Detection.Persistance.Models.StoreModels.PlanWorkTime import PlanWorkTime as ScheduleModel 

class ScheduleMapper:

    def map_to_domain_model(self, db_model: ScheduleModel) -> Schedule:
        if db_model is None: return None
        if not isinstance(db_model, ScheduleModel):
            raise ValueError(db_model)   
        holidays = []
        for holiday_db in db_model.plan_days:
            holidays.append(holiday_db.date)

        schedule = Schedule(
            date_assignment=db_model.write_date,
            holidays=holidays
        )
        return schedule