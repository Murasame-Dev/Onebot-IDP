import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import BindPage from '../views/BindPage.vue'
import AuthorizePage from '../views/AuthorizePage.vue'
import BindingsManagement from '../views/BindingsManagement.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/bind/:bindCode',
    name: 'Bind',
    component: BindPage,
    props: true
  },
  {
    path: '/oauth/authorize',
    name: 'Authorize',
    component: AuthorizePage
  },
  {
    path: '/admin/bindings',
    name: 'BindingsManagement',
    component: BindingsManagement
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
