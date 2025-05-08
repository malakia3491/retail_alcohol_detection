import PlanogramComplianceReport from "@/views/Reports/PlanogramComplianceReport.vue"
import PlanogramUsageReportView from "@/views/Reports/PlanogramUsageReportView.vue"

export const reportsRouters = [
  { path: '/reports/planogram_compliance', name: 'PlanogramCompliance', component: PlanogramComplianceReport, meta: { requiresAuth: true } },
  { path: '/reports/planogram_usage', name: 'PlanogramUsage', component: PlanogramUsageReportView, meta: { requiresAuth: true } },
]