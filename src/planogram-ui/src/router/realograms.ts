import ActualRealogramView from "@/views/Realogram/ActualRealogramView.vue";
import RealogramsView from "@/views/Realogram/RealogramsView.vue";
import RealogramDetailsView from "@/views/Realogram/RealogramDetailsView.vue";

export const realogramsRoutes = [
  { path: '/realograms/actual/', name: 'ActualRealograms', component: ActualRealogramView, meta: { requiresAuth: true } },
  { path: '/realograms/', name: 'Realograms', component: RealogramsView, meta: { requiresAuth: true } },
  { path: '/stores/:store_id/realograms/:id', name: 'RealogramDetails', component: RealogramDetailsView, meta: { requiresAuth: true } },
];