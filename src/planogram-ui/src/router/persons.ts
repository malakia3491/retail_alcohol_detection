import LoginView from '@/views/Person/LoginView.vue'
import ProfileView from '@/views/Person/ProfileView.vue'

export const personsRoutes = [
  { path: '/profile', name: 'Profile', component: ProfileView, meta: { requiresAuth: true } },
  { path: '/login', name: 'Login', component: LoginView },
]