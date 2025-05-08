export interface PlanogramComplianceReportRow {
    total_notifications_empty: number;
    total_notifications_mismatch: number;
    resolved_on_time_empty: number;
    resolved_on_time_mismatch: number;
    unresolved_empty_no_stock: number;
    avg_reaction_time_empty_min: number;
    avg_reaction_time_mismatch_min: number;
    avg_planogram_accordance_percent: number;
}

export interface PlanogramComplianceReport {
    rows: Record<string, Record<string, PlanogramComplianceReportRow>>;
}

export interface PlanogramUsageReportRow {
    store_name: string;
    approval_date: string;       // ISO date string
    approver_name: string;
    calibration_date: string;    // ISO date string
    calibrator_name: string;
    avg_accordance_percent: number;
  }
  
  export interface PlanogramUsageReport {
    rows: Record<string, Record<string, PlanogramUsageReportRow>>;
  }