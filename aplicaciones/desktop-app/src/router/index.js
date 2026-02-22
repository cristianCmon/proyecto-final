import { createRouter, createWebHashHistory } from 'vue-router';

// Importamos las vistas
import Login from '../views/LoginUsuario.vue';
import Registro from '../views/RegistroUsuario.vue';
import Layout from '../layouts/AutorizacionLayout.vue';
import Dashboard from '../views/Dashboard.vue';

// Definimos rutas
const routes = [
  // VISTAS DE ACCESO
  {
    path: '/',
    component: Layout,
    children: [
      { path: '', name: 'Login', component: Login },
      { path: 'registro', name: 'Registro', component: Registro },
    ]
  },
  // VISTA APLICACIÓN
  { path: '/dashboard', name: 'Dashboard', component: Dashboard }
];

// Creamos la instancia del Router
const router = createRouter({
  // AQUÍ ESTÁ LA CLAVE PARA ELECTRON:
  history: createWebHashHistory(),
  routes
});

// COMPROBACIÓN DE SEGURIDAD, FRENA A USUARIOS SIN CREDENCIALES
router.beforeEach((to, from, next) => {
  const vistasPublicas = ['Login', 'Registro'];
  const requiereAutorizacion = !vistasPublicas.includes(to.name);
  const estaLogueado = sessionStorage.getItem('tokenUsuario');

  if (requiereAutorizacion && !estaLogueado) {
    // SI EL USUARIO INTENTA ACCEDER A UNA VISTA QUE REQUIERE CREDENCIALES, VUELVE AL LOGIN
    next({ name: 'Login' });

  } else {
    // SINO SIGUE ADELANTE CON NORMALIDAD
    next();
  }
});

export default router;