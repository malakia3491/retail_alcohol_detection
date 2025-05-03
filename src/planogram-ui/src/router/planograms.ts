import CreatePlanogramView from '@/views/Planogram/CreatePlanogramView.vue';


export const planogramsRoutes = [
  { path: '/planogram/create/:order_id/:shelving_id', name: 'CreatePlanogram', component: CreatePlanogramView },
];