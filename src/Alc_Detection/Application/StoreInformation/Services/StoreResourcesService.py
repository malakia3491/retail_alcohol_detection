import traceback
from typing import Dict
from datetime import datetime
from collections import defaultdict
from fastapi import HTTPException, status

from Alc_Detection.Application.IncidentManagement.Settings import Settings
from Alc_Detection.Application.Mappers.StoreMapper import StoreMapper
from Alc_Detection.Application.Requests.Reports import PlanogramComplianceReport, PlanogramComplianceReportRow, PlanogramUsageReport, PlanogramUsageReportRow
from Alc_Detection.Application.Requests.Requests import AddStoresRequest
from Alc_Detection.Application.Requests.Responses import StoresResponse
from Alc_Detection.Domain.Date.extensions import Period
from Alc_Detection.Domain.Extentions.Utils import adjust_day_edge
from Alc_Detection.Domain.Shelf.DeviationManagment.Incident import Incident
from Alc_Detection.Domain.Store.Store import Store
from Alc_Detection.Persistance.Repositories.StoreRepository import StoreRepository

class StoreResourcesService:
    def __init__(
        self,
        store_repository: StoreRepository,
        store_mapper: StoreMapper,
        settings: Settings
    ):
        self._store_repository = store_repository
        self._store_mapper = store_mapper
        self._settings = settings
    
    async def get_store_by_login(self, login: str) -> Store:
        store = await self._store_repository.get_by_login(login)
        if not store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Store with login {login} not found."
            )
        return store
        
    async def get_stores(self) -> StoresResponse:
        stores = await self._store_repository.get_all_not_office()
        return StoresResponse(
            stores=[self._store_mapper.map_to_response_model(store) for store in stores ]
        )
    
    async def add_stores(self, request: AddStoresRequest) -> str:
        try:
            stores = [Store(name=store.name) for store in request.stores]
            count_added_records = await self._store_repository.add(*stores)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())      

    async def load_stores(self, stores: list[Store]) -> str:
        try:
            count_added_records = await self._store_repository.add(*stores)
            return f"Succsessfully. Added {count_added_records} records."
        except Exception as ex:
            print(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=ex.__str__())   
        
    async def generate_planogram_compliance_report(self, start: datetime, end: datetime) -> PlanogramComplianceReport:
        rows = defaultdict(dict)
        stores = await self._store_repository.get_all_not_office()
        start = adjust_day_edge(dt=start, end_of_day=False)
        end = adjust_day_edge(dt=end, end_of_day=True)
        for store in stores:
            for shift in store.shifts:
                incidents = shift.get_incidents_by_period(Period(start=start, end=end)) 
                empty_incidents = [inc for inc in incidents if inc.type == "Пустоты"]
                no_product_incidents = [inc for inc in incidents if inc.type == "Нет товаров"]
                mismatch_incidents = [inc for inc in incidents if inc.type == "Несоблюдения планограммы"]

                total_empty = len(empty_incidents)
                total_mismatch = len(mismatch_incidents)

                resolved_empty = sum(
                    1 for inc in empty_incidents
                    if inc.is_resolved and inc.reaction_time <= self._settings.REACTION_TIME
                )
                resolved_mismatch = sum(
                    1 for inc in mismatch_incidents
                    if inc.is_resolved and inc.reaction_time <= self._settings.REACTION_TIME
                )

                unresolved_empty_no_stock = len(no_product_incidents)

                def avg_reaction(inc_list: list[Incident]) -> float | None:
                    times = [inc.reaction_time / 60 for inc in inc_list if inc.is_resolved]
                    return sum(times) / len(times) if times else None

                avg_rt_empty = avg_reaction(empty_incidents)
                avg_rt_mismatch = avg_reaction(mismatch_incidents)

                accords = [
                    r.accordance for r in store.realograms
                    if r.shelving in {inc.shelving for inc in incidents}
                    and shift.work_time.start <= r.create_date.time() <= shift.work_time.end
                ]
                avg_accord = sum(accords) / len(accords) if accords else None

                rows[store.name][shift.name] = PlanogramComplianceReportRow(
                    total_notifications_empty=total_empty,
                    total_notifications_mismatch=total_mismatch,
                    resolved_on_time_empty=resolved_empty,
                    resolved_on_time_mismatch=resolved_mismatch,
                    unresolved_empty_no_stock=unresolved_empty_no_stock,
                    avg_reaction_time_empty_min=avg_rt_empty,
                    avg_reaction_time_mismatch_min=avg_rt_mismatch,
                    avg_planogram_accordance_percent=avg_accord
                )

        return PlanogramComplianceReport(rows=rows)
    
    async def generate_planogram_usage_report(
            self, 
            start: datetime, 
            end: datetime
        ) -> PlanogramUsageReport:
            stores = await self._store_repository.get_all_not_office()
            rows: Dict[str, Dict[str, PlanogramUsageReportRow]] = defaultdict()
            start = adjust_day_edge(dt=start, end_of_day=False)
            end = adjust_day_edge(dt=end, end_of_day=True)
            period = Period(start=start, end=end)
            
            for store in stores:
                using_planograms_data = store.get_using_planograms_by_period(period)
                if not using_planograms_data: continue
                for planogram in using_planograms_data:
                    (creator, create_date), pg_period = using_planograms_data[planogram]
                    realograms = store.get_realograms_by_shelving_period(planogram.shelving, pg_period)
                    accords = [r.accordance for r in realograms]
                    avg_accord = sum(accords) / len(accords) if accords else 0.0
                    shelving_name = planogram.shelving.name
                    realograms_count = len(realograms)
                    row = PlanogramUsageReportRow(
                        shelving_name=shelving_name,
                        planogram_date=planogram.create_date,
                        store_name=store.name,
                        approval_date=planogram.approval_date,
                        approver_name=planogram.approver.name,
                        calibration_date=create_date,
                        calibrator_name=creator.name,
                        avg_accordance_percent=avg_accord,
                        count=realograms_count)
                    rows[store.name][str(planogram.id)] = row
            return PlanogramUsageReport(rows=rows)