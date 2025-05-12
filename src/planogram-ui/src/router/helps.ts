import NotificationHelpView from "@/views/Help/NotificationHelpView.vue"

export const helpsRoutes = [
  { path: '/help/notification', name: 'NotificationHelp', component: NotificationHelpView, meta: { requiresAuth: true } },
]