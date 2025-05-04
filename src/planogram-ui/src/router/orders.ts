import AllOrdersListView from '@/views/PlanogramOrder/AllOrdersListView.vue';
import ActualOrdersListView from '@/views/PlanogramOrder/ActualOrdersListView.vue';
import OrderDetailsView from '@/views/PlanogramOrder/OrderDetailsView.vue';

export const ordersRoutes = [
  { path: '/orders', name: 'AllOrders', component: AllOrdersListView, meta: { requiresAuth: true } },
  { path: '/orders/active', name: 'ActiveOrders', component: ActualOrdersListView, meta: { requiresAuth: true } },
  { path: '/orders/:id', name: 'OrderDetail', component: OrderDetailsView, props: true, meta: { requiresAuth: true } },
]