from uuid import UUID
from pydantic import BaseModel
from datetime import datetime, time
from typing import Dict, List, Optional

class PlanogramComplianceReportRow(BaseModel):
    total_notifications_empty: int
    total_notifications_mismatch: int
    resolved_on_time_empty: int
    resolved_on_time_mismatch: int
    unresolved_empty_no_stock: int
    avg_reaction_time_empty_min: Optional[float] 
    avg_reaction_time_mismatch_min: Optional[float]
    avg_planogram_accordance_percent: Optional[float]                    

class PlanogramComplianceReport(BaseModel):
    rows: Dict[str, Dict[str, PlanogramComplianceReportRow]]
    
class PlanogramUsageReportRow(BaseModel):
    shelving_name: str
    planogram_date: datetime
    store_name: str
    approval_date: datetime
    approver_name: str
    calibration_date: datetime
    calibrator_name: str
    avg_accordance_percent: float
    count: int

class PlanogramUsageReport(BaseModel):
    rows: Dict[str, Dict[str, Dict[str, PlanogramUsageReportRow]]]