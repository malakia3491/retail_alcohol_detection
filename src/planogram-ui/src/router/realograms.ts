import ActualRealogramView from "@/views/Realogram/ActualRealogramView.vue";

export const realogramsRoutes = [
  { path: '/realograms/actual/', name: 'ActualRealograms', component: ActualRealogramView, meta: { requiresAuth: true } },
];