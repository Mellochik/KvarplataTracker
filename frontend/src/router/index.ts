import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'dashboard',
    component: () => import('../views/Dashboard.vue'),
  },
  {
    path: '/readings',
    name: 'readings',
    component: () => import('../views/Readings.vue'),
  },
  {
    path: '/tariffs',
    name: 'tariffs',
    component: () => import('../views/Tariffs.vue'),
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})