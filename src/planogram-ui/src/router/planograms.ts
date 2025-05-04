import CreatePlanogramView from '@/views/Planogram/CreatePlanogramView.vue';
import PlanogramDetailsView from '@/views/Planogram/PlanogramDetailsView.vue';

export const planogramsRoutes = [
  { path: '/planogram/:order_id/:planogram_id', name: 'PlanogramDetail', component: PlanogramDetailsView, meta: { requiresAuth: true } },
  { path: '/planogram/create/:order_id/:shelving_id', name: 'CreatePlanogram', component: CreatePlanogramView, meta: { requiresAuth: true } },
];