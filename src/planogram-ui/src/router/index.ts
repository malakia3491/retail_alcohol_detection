import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { ordersRoutes }    from './orders'
import { planogramsRoutes } from './planograms'
import { productsRoutes } from './products'
import { personsRoutes } from './persons'
import { realogramsRoutes } from './realograms'
import { authStore } from '@/auth/store'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: "Home", component: HomeView , meta: { requiresAuth: true } },
  ...ordersRoutes,
  ...planogramsRoutes,
  ...productsRoutes,
  ...personsRoutes,
  ...realogramsRoutes,
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const isAuthRequired = to.meta.requiresAuth;
  await authStore.checkAuth();
  
  if (isAuthRequired && !authStore.isAuthenticated) {
    return { name: 'Login' };
  }
  
  if (!isAuthRequired && authStore.isAuthenticated) {
    return { name: 'Home' };
  }
});

export default router 