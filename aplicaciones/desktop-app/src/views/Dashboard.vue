<template>
  <div class="dashboard-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <img src="../assets/mancuerna.png" alt="Logo" class="mini-logo">
        <h3>GYM EX</h3>
      </div>
      
      <nav class="menu">
        <a href="#" class="menu-item active">
          <i class="icon">🏠</i> Inicio
        </a>
        <a href="#" class="menu-item">
          <i class="icon">🏋️</i> Actividades
        </a>

        <div v-if="usuario.rol === 'administrador'" class="admin-section">
          <p class="section-label">Gestión</p>
          <a href="#" class="menu-item"><i>👥</i> Usuarios</a>
          <a href="#" class="menu-item"><i>📊</i> Reportes</a>
        </div>

        <div v-if="usuario.rol === 'cliente'" class="client-section">
          <p class="section-label">Mi Cuenta</p>
          <a href="#" class="menu-item"><i>📅</i> Mis Reservas</a>
        </div>
      </nav>

      <button @click="cerrarSesion" class="btn-logout">
        Cerrar Sesión
      </button>
    </aside>

    <main class="main-content">
      <header class="top-bar">
        <div class="page-info">
          <h2>Panel de Control</h2>
          <p>Bienvenido de nuevo, <strong>{{ usuario.nombre_usuario }}</strong></p>
        </div>
        <div class="user-badge" :class="usuario.rol">
          {{ usuario.rol }}
        </div>
      </header>

      <section class="scrollable-area">
        <div class="stats-grid">
          <div class="card">
            <h4>Estado</h4>
            <div class="status-indicator">Activo</div>
          </div>
          <div class="card">
            <h4>Próxima Clase</h4>
            <p>No tienes clases hoy</p>
          </div>
          <div class="card">
            <h4>Notificaciones</h4>
            <p>3 mensajes nuevos</p>
          </div>
        </div>

        <div class="content-card mt-20">
          <h3>Próximas Actividades</h3>
          <p>Cargando actividades del gimnasio...</p>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
  import { apiFetch } from '../api';

  export default {
    data() {
      return {
        usuario: {
          nombre_usuario: sessionStorage.getItem('nombre_usuario') || 'Usuario',
          rol: sessionStorage.getItem('rol') || 'cliente'
        },
        actividades: [], // CONTENIDO DEL BACKEND
        cargando: true
      }
    },
    // SE EJECUTA AL CARGAR LA VISTA
    async mounted() {
      await this.obtenerActividades();
    },
    
    methods: {
      async obtenerActividades() {
        try {
          const data = await apiFetch('/actividades', { method: 'GET' });
          this.actividades = data;

        } catch (err) {
          console.error("Error cargando actividades:", err);

        } finally {
          this.cargando = false;
        }
      },

      cerrarSesion() {
        // Limpiamos info guardada en almacenamiento y volvemos al login
        sessionStorage.clear();
        this.$router.push({name: 'Login'});
      }
    }
  }
</script>

<style scoped>
  @import "../styles/dashboard.css";
</style>