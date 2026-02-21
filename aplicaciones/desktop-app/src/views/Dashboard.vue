<template>
  <div class="dashboard-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h3>GymApp</h3>
      </div>
      <nav class="menu">
        <a href="#" class="active">Inicio</a>
        <a href="#">Actividades</a>
        <a href="#">Mis Reservas</a>
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
</template>

<script>
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
</script>

<style scoped>
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
</style>