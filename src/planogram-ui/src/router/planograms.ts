import CreatePlanogramView from '@/views/Planogram/CreatePlanogramView.vue';
import PlanogramDetailsView from '@/views/Planogram/PlanogramDetailsView.vue';
import ActualPlanogramsView from '@/views/Planogram/ActualPlanogramsView.vue';
import UpdatePlanogramView from '@/views/Planogram/UpdatePlanogramView.vue';
import CalibratePlanogramView from '@/views/Planogram/CalibratePlanogramView.vue';

export const planogramsRoutes = [
  { path: '/planogram/:order_id/:planogram_id', name: 'PlanogramDetail', component: PlanogramDetailsView, meta: { requiresAuth: true } },
  { path: '/planogram/create/:order_id/:shelving_id', name: 'CreatePlanogram', component: CreatePlanogramView, meta: { requiresAuth: true } },
  { path: '/planograms/actual/', name: 'ActualPlanograms', component: ActualPlanogramsView, meta: { requiresAuth: true } },
  { path: '/planogram/update/:order_id/:planogram_id', name: 'UpdatePlanogram', component: UpdatePlanogramView, meta: { requiresAuth: true } },
  { path: '/planogram/calibrate/:planogram_id', name: 'CalibratePlanogram', component: CalibratePlanogramView, meta: { requiresAuth: true } },
];