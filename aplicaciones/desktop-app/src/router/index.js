import { createRouter, createWebHashHistory } from 'vue-router';

// Importamos las vistas
import Login from '../views/LoginUsuario.vue';
import Registro from '../views/RegistroUsuario.vue';
import Layout from '../layouts/AutorizacionLayout.vue';
import Dashboard from '../views/Dashboard.vue';

// Definimos rutas
const routes = [
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', name: 'Login', component: Login },
      { path: 'registro', name: 'Registro', component: Registro },
      { path: 'dashboard', name: 'Dashboard', component: Dashboard }
    ]
  }
  // {
  //   path: '/',
  //   name: 'Login',
  //   component: Login
  // },
  // {
  //   path: '/registro',
  //   name: 'Registro',
  //   component: Registro
  // },
  // {
  //   path: '/dashboard',
  //   name: 'Dashboard',
  //   // Carga perezosa (lazy loading) para mejorar el rendimiento
  //   component: () => import('../views/Dashboard.vue') 
  // }
];

// Creamos la instancia del Router
const router = createRouter({
  // AQUÍ ESTÁ LA CLAVE PARA ELECTRON:
  history: createWebHashHistory(),
  routes
});

export default router;