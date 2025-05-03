import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { ordersRoutes }    from './orders'
import { planogramsRoutes } from './planograms'
import { productsRoutes } from './products'

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', component: HomeView },
  ...ordersRoutes,
  ...planogramsRoutes,
  ...productsRoutes,
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 