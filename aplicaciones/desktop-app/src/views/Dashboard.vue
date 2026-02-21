<!-- <template>
  <div class="dashboard-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h3>GymApp</h3>
      </div>
      <nav class="menu">
        <a href="#" class="active">Inicio</a>
        <a href="#">Calendario de Clases</a>

        <div v-if="usuario.rol === 'administrador'">
          <hr> <a href="#">Gestionar Actividades</a>
          <a href="#">Listado de Clientes</a>
          <a href="#">Reporte de Ingresos</a>
        </div>

        <div v-if="usuario.rol === 'cliente'">
          <a href="#">Mi Perfil</a>
          <a href="#">Historial de Pagos</a>
        </div>
      </nav>
      <button @click="cerrarSesion" class="btn-logout">Cerrar Sesión</button>
    </aside>

    <main class="content">
      <header class="top-bar">
        <h2>Panel de Control</h2>
        <div class="user-info">
          <span>Bienvenido, <strong>{{ usuario.nombre_usuario }}</strong></span>
          <span class="badge">{{ usuario.rol }}</span>
        </div>
      </header>

      <section class="stats-grid">
        <div class="stat-card">
          <h4>Próximas Sesiones</h4>
          <p>Explora las actividades disponibles para hoy.</p>
        </div>
        <div class="stat-card">
          <h4>Estado de Suscripción</h4>
          <p style="color: green; font-weight: bold;">Activa</p>
        </div>
      </section>
    </main>
  </div>
</template> -->

<!-- <script>
export default {
  data() {
    return {
      usuario: {
        nombre_usuario: sessionStorage.getItem('nombre_usuario') || 'Usuario',
        rol: sessionStorage.getItem('rol') || 'Cliente'
      }
    }
  },
  methods: {
    cerrarSesion() {
      // Limpiamos info guardada en almacenamiento y volvemos al login
      sessionStorage.clear();
      this.$router.push({name: 'Login'});
    }
  }
}
</script> -->

<!-- <style scoped>
.dashboard-container {
  display: flex;
  width: 100vw;
  height: 100vh;
  background-color: #f8fafc;
}

.sidebar {
  width: 250px;
  background-color: #1e293b;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 20px;
}

.menu {
  flex-grow: 1;
  margin-top: 30px;
}

.menu a {
  display: block;
  color: #94a3b8;
  text-decoration: none;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 5px;
}

.menu a.active, .menu a:hover {
  background-color: #334155;
  color: white;
}

.content {
  flex-grow: 1;
  padding: 30px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 20px;
  margin-bottom: 30px;
}

.badge {
  background-color: #e2e8f0;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-left: 10px;
  text-transform: uppercase;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.btn-logout {
  background-color: #ef4444;
  margin-top: auto;
}
</style> -->

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

      <button @click="handleLogout" class="btn-logout">
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
export default {
  data() {
    return {
      usuario: {
        nombre_usuario: sessionStorage.getItem('nombre_usuario') || 'Usuario',
        rol: sessionStorage.getItem('rol') || 'cliente'
      }
    }
  },
  methods: {
    handleLogout() {
      sessionStorage.clear();
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
/* Contenedor principal que ocupa toda la ventana de Electron */
.dashboard-wrapper {
  display: flex;
  width: 100vw;
  height: 100vh;
  overflow: hidden; /* Evita scroll en la ventana principal */
  background-color: #f1f5f9;
}

/* Sidebar fija a la izquierda */
.sidebar {
  width: 280px;
  background-color: #0f172a;
  color: white;
  display: flex;
  flex-direction: column;
  padding: 24px;
  flex-shrink: 0; /* Evita que se encoja */
}

.sidebar-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 40px;
}

.mini-logo {
  width: 32px;
  filter: brightness(0) invert(1);
}

.section-label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 20px 0 10px 12px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #94a3b8;
  text-decoration: none;
  padding: 12px;
  border-radius: 8px;
  transition: all 0.2s;
}

.menu-item:hover, .menu-item.active {
  background-color: #1e293b;
  color: white;
}

/* Área de contenido */
.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.top-bar {
  background: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  z-index: 10;
}

.user-badge {
  padding: 6px 14px;
  border-radius: 99px;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
}
.user-badge.administrador { background: #fee2e2; color: #ef4444; }
.user-badge.cliente { background: #dcfce7; color: #22c55e; }

/* Área con scroll para que el contenido no se pierda */
.scrollable-area {
  padding: 40px;
  overflow-y: auto;
  flex-grow: 1;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.content-card {
  background: white;
  padding: 30px;
  border-radius: 12px;
  min-height: 400px;
  border: 1px solid #e2e8f0;
}

.mt-20 { margin-top: 20px; }

.btn-logout {
  background-color: #ef4444;
  color: white;
  margin-top: auto;
  padding: 12px;
  border-radius: 8px;
  font-weight: bold;
}
</style>