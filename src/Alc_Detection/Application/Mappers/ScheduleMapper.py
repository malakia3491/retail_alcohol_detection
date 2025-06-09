from datetime import datetime
from Alc_Detection.Domain.Store.PersonManagment.Schedule import Schedule
from Alc_Detection.Domain.Store.PersonManagment.Shift import Shift
from Alc_Detection.Persistance.Models.StoreModels.PlanWorkTime import PlanWorkTime as ScheduleModel 
from Alc_Detection.Application.Requests.person_management import Schedule as ScheduleApiModel
from Alc_Detection.Persistance.Models.Models import PlanSchedule as PlanScheduleModel 

class ScheduleMapper:
    
    def map_to_domain_model(self, db_model: ScheduleModel) -> Schedule:
        if db_model is None: return None
        if not isinstance(db_model, ScheduleModel):
            raise ValueError(db_model)   
        holidays = []
        for holiday_db in db_model.plan_days:
            holidays.append(holiday_db.date)

        schedule = Schedule(
            retail_id=db_model.retail_id,
            date_assignment=db_model.write_date,
            holidays=holidays,
            date_from=db_model.date_from,
            date_to=db_model.date_to
        )
        return schedule
    
    def map_request_to_domain_model(self, req_model: ScheduleApiModel) -> Schedule:
        if req_model is None: return None
        if not isinstance(req_model, ScheduleApiModel):
            raise ValueError(req_model)   
        holidays = []
        for holiday_db in req_model.holidays:
            holidays.append(holiday_db.date_day)

        schedule = Schedule(
            date_assignment=req_model.write_day,
            holidays=holidays,
            date_from=req_model.date_from,
            date_to=req_model.date_to
        )
        return schedule
    
    def map_to_db_model(self, shift: Shift, domain_model: Schedule) -> ScheduleModel:
        if domain_model is None: return None
        if not isinstance(domain_model, Schedule):
            raise ValueError(domain_model)        
        plan_days = []
        for day in domain_model.days:
            plan_day = PlanScheduleModel(
                date=day
            )
            plan_days.append(plan_day)        
        return ScheduleModel(
            store_shift_id=shift.id,
            retail_id=shift.retail_id,
            write_date=domain_model.date_assignment,
            date_from=domain_model.period.start,
            date_to=domain_model.period.end,
            plan_days=plan_days,  
        )