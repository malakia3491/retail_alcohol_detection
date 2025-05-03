import AllOrdersListView from '@/views/PlanogramOrder/AllOrdersListView.vue';
import ActualOrdersListView from '@/views/PlanogramOrder/ActualOrdersListView.vue';
import OrderDetailsView from '@/views/PlanogramOrder/OrderDetailsView.vue';

export const ordersRoutes = [
  { path: '/orders', name: 'AllOrders', component: AllOrdersListView },
  { path: '/orders/active', name: 'ActiveOrders', component: ActualOrdersListView },
  { path: '/orders/:id', name: 'OrderDetail', component: OrderDetailsView, props: true },
]