import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/LoginView.vue'),
      meta: { noAuth: true },
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        { path: '', name: 'Generator', component: () => import('@/views/GeneratorView.vue') },
        { path: 'history', name: 'History', component: () => import('@/views/HistoryView.vue') },
        { path: 'environments', name: 'Environments', component: () => import('@/views/EnvironmentsView.vue') },
        { path: 'optimizer', name: 'Optimizer', component: () => import('@/views/OptimizerView.vue') },
        { path: 'installer', name: 'Installer', component: () => import('@/views/InstallerView.vue') },
        { path: 'rman', name: 'RMAN', component: () => import('@/views/RmanView.vue') },
        { path: 'templates', name: 'Templates', component: () => import('@/views/TemplatesView.vue') },
        { path: 'settings', name: 'Settings', component: () => import('@/views/SettingsView.vue') },
        { path: 'audit', name: 'AuditLog', component: () => import('@/views/AuditLogView.vue') },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.noAuth || token) {
    next()
  } else {
    next('/login')
  }
})

export default router
