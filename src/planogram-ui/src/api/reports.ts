import axios from 'axios';

import {base_url} from '@/api/config';
import type { PlanogramComplianceReport, PlanogramUsageReport } from '@/types'  

const reports_url = `${base_url}/retail/reports`;

export const get_planogram_compliance_report = async (start: string, end: string): Promise<PlanogramComplianceReport> => {
    const url = `${reports_url}/planogram_compliance_report/${start}/${end}`;
    const result = await axios.get<PlanogramComplianceReport>(url);
    const realograms = result.data
    return realograms;
}

export const get_planogram_usage_report = async (start: string, end: string): Promise<PlanogramUsageReport> => {
    const url = `${reports_url}/planogram_usage_report/${start}/${end}`;
    const resp = await axios.get<PlanogramUsageReport>(url);
    return resp.data;
}