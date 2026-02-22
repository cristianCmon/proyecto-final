<template>
  <div class="dashboard-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <img src="../assets/mancuerna.png" alt="Logo" class="mini-logo">
        <h3>GYM EX</h3>
      </div>
      <nav class="menu">
        <!-- IMPORTANTE click.prevent PARA QUE EL ENRUTADOR NO ACTUALICE Y LLEVE A VISTA LOGIN -->
        <a href="#" @click.prevent="pestanaActiva = 'actividades'" :class="['menu-item', { active: pestanaActiva === 'actividades' }]">
          <i>🏋️</i> Actividades
        </a>
        <a href="#" @click.prevent="pestanaActiva = 'sesiones'" :class="['menu-item', { active: pestanaActiva === 'sesiones' }]">
          <i>📅</i> Sesiones / Calendario
        </a>

        <div v-if="usuario.rol === 'administrador'" class="admin-section">
          <p class="section-label">Gestión</p>
          <a href="#" class="menu-item"><i>👥</i> Usuarios</a>
        </div>
      </nav>
      <button @click="cerrarSesion" class="btn-logout">Cerrar Sesión</button>
    </aside>

    <main class="main-content">
      <header class="top-bar">
        <div class="page-info">
          <h2>{{ tituloPestana }}</h2>
          <p>Bienvenido, <strong>{{ usuario.nombre_usuario }}</strong></p>
        </div>
        <div class="user-badge" :class="usuario.rol">{{ usuario.rol }}</div>
      </header>

      <section class="scrollable-area">

        <!-- TAB ACTIVIDADES -->
        <div v-if="pestanaActiva === 'actividades'" class="tab-content">
          <div class="content-card">
            <div class="header-section">
              <h3>Oferta de Actividades</h3>
              <!-- FORZAMOS VARIABLE editando A FALSE -->
              <button v-if="usuario.rol === 'administrador'" @click="editando = false; mostrarModalActividad = true" class="btn-add">+ Nueva Actividad</button>
            </div>

            <div v-if="cargando" class="loader">Cargando catálogo...</div>

            <div v-else class="actividades-grid">
              <div v-for="act in actividades" :key="act.id" class="act-card">
                <div class="act-info">
                  <h4>{{ act.nombre }}</h4>
                  <p class="descripcion">{{ act.descripcion }}</p>
                  <!-- <div class="meta">
                    <span>📍 {{ act.aula }}</span>
                    <span>👥 {{ act.capacidad_maxima }} plazas</span>
                  </div> -->
                </div>
                
                <div v-if="usuario.rol === 'administrador'" class="act-actions">
                  <button @click="generarSesiones(act.id)" class="btn-generate">
                    🗓️ Generar Sesiones (7 días)
                  </button>
                  <div class="admin-btns-row">
                    <button @click="modificarActividad(act)" class="btn-edit">✏️</button>
                    <button @click="eliminarActividad(act.id)" class="btn-delete">🗑️</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- TAB SESIONES -->
        <div v-if="pestanaActiva === 'sesiones'" class="tab-content">
          <div class="content-card">
            <div class="header-section">
              <h3>Próximas Sesiones</h3>
              <p v-if="usuario.rol === 'cliente'">Reserva tu plaza en las clases disponibles</p>
            </div>

            <div v-if="sesiones.length === 0" class="empty-state">
              <p>No hay sesiones programadas. El administrador debe generar sesiones desde la pestaña de Actividades.</p>
            </div>

            <div v-else class="sesiones-table-container">
              <table class="sesiones-table">
                <thead>
                  <tr>
                    <th>Actividad</th>
                    <th>Día</th>
                    <th>Horario</th>
                    <th>Disponibilidad</th>
                    <th>Estado</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="sesion in sesiones" :key="sesion.id">
                    <td><strong>{{ sesion.nombre }}</strong></td>
                    <td>{{ formatearFecha(sesion.fecha) }}</td>
                    <td>{{ sesion.hora_inicio }} - {{ sesion.hora_fin }}</td>
                    <td>
                      <div class="capacity-bar">
                        <span class="text">{{ sesion.capacidad_actual }} / {{ sesion.capacidad_maxima }}</span>
                      </div>
                    </td>
                    <td><span :class="['status-pill', sesion.estado]">{{ sesion.estado }}</span></td>
                    <td>
                      <button v-if="usuario.rol === 'cliente'" @click="reservarSesion(sesion.id)" 
                        :disabled="sesion.capacidad_actual >= sesion.capacidad_maxima || sesion.estado === 'cancelada'"
                        :class="['btn-reserve-small', { 'btn-full': sesion.capacidad_actual >= sesion.capacidad_maxima }]">
                        Reservar
                      </button>
                      <button v-if="usuario.rol === 'administrador'" @click="cancelarSesion(sesion.id)" class="btn-delete-small">
                        Anular
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </section>
    </main>

    <!-- MODAL FORMULARIO ACTIVIDAD -->
    <div v-if="mostrarModalActividad" class="modal-overlay">
      <div class="modal-card">
        <header class="modal-header">
          <h3>{{ editando ? 'Modificar Actividad' : 'Configuración Nueva Actividad' }}</h3>
          </header>

        <form @submit.prevent="guardarActividad" class="modal-form">
          <div class="form-group">
            <label>Nombre</label>
            <input v-model="nuevaActividad.nombre" placeholder="Ej: Pilates Avanzado" required>
          </div>

          <div class="form-group">
            <label>Descripción</label>
            <textarea v-model="nuevaActividad.descripcion" placeholder="Detalles de la actividad..."></textarea>
          </div>

          <div class="form-group">
            <label>Capacidad Máxima</label>
            <input v-model.number="nuevaActividad.capacidad_maxima" type="number" min="1" step="1" required>
          </div>

          <div class="horarios-section">
            <h4>Horarios Semanales (Plantilla)</h4>
            <div v-for="(h, index) in nuevaActividad.horario" :key="index" class="horario-item">
              
              <select v-model="h.dia">
                <option :value="h.dia">{{ h.dia }}</option>
                <option v-for="d in diasDisponibles" :key="d" :value="d">{{ d }}</option>
              </select>

              <input type="time" v-model="h.hora_inicio" required>
              <span>a</span>
              <input type="time" v-model="h.hora_fin" required>
              <button type="button" @click="quitarHorario(index)" class="btn-remove-h">×</button>
            </div>

            <button v-if="aceptaMasHorarios" type="button" @click="incluirHorario" class="btn-add-h">
              + Añadir Horario
            </button>
          </div>

          <div class="modal-actions">
            <button type="button" @click="cerrarLimpiarModal" class="btn-cancel">Cancelar</button>
            <button type="submit" class="btn-save">{{ editando ? 'Actualizar Cambios' : 'Crear Actividad' }}</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<script>
import { apiFetch } from '../api';

export default {
  data() {
    return {
      pestanaActiva: 'actividades', // 'actividades' o 'sesiones'
      usuario: {
        id: sessionStorage.getItem('idUsuario'),
        nombre_usuario: sessionStorage.getItem('nombre_usuario') || 'Usuario',
        rol: sessionStorage.getItem('rol') || 'cliente'
      },
      actividades: [],
      sesiones: [],
      cargando: true,

      mostrarModalActividad: false,
      dias: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
      nuevaActividad: {
        nombre: '',
        descripcion: '',
        capacidad_maxima: 10,
        horario: [] // Lista de objetos { dia, hora_inicio, hora_fin }
      },

      editando: false,
      idActividadEditable: null,
    }
  },

  computed: {
    tituloPestana() {
      return this.pestanaActiva === 'actividades' ? 'Catálogo de Actividades' : 'Calendario de Sesiones';
    },

    // FILTRA DÍAS DISPONIBLES EN FORMULARIO ACTIVIDAD
    diasDisponibles() {
      // Obtenemos los días que ya están en el array de horarios
      const diasSeleccionados = this.nuevaActividad.horario.map(h => h.dia);
      // Retornamos solo los que no están en esa lista
      return this.dias.filter(d => !diasSeleccionados.includes(d));
    },

    // DÍAS MÁXIMOS PARA UNA ACTIVIDAD
    aceptaMasHorarios() {
      return this.nuevaActividad.horario.length < 7;
    }
  },

  async mounted() {
    await this.refrescarDashboard();
  },

  methods: {
    async refrescarDashboard() {
      this.cargando = true;
      console.log(this.usuario);
      try {
        const [dataAct, dataSes] = await Promise.all([
          apiFetch('/actividades'),
          apiFetch('/sesiones')
        ]);

        this.actividades = dataAct;
        console.log(this.actividades);
        this.sesiones = dataSes;
        console.log(this.sesiones);

      } catch (err) {
        console.error("Error al sincronizar:", err);

      } finally {
        this.cargando = false;
      }
    },

    async generarSesiones(id) {
      try {
        const res = await apiFetch(`/actividades/${id}/sesiones`, { method: 'POST' });
        alert(res.mensaje);
        await this.refrescarDashboard();
        this.pestanaActiva = 'sesiones'; // Lleva automáticamente a ver las sesiones creadas

      } catch (err) {
        alert("Error: " + (err.ERROR || "No se pudo generar"));
      }
    },

    formatearFecha(fechaStr) {
      const opciones = { weekday: 'long', day: 'numeric', month: 'long' };
      return new Date(fechaStr).toLocaleDateString('es-ES', opciones);
    },

    cerrarSesion() {
      sessionStorage.clear();
      this.$router.push('/');
    },

    incluirHorario() {
      if (this.aceptaMasHorarios) {
        this.nuevaActividad.horario.push({
          dia: this.diasDisponibles[0],
          hora_inicio: '09:00',
          hora_fin: '10:00'
        });

      } else {
        alert("Ya has programado todos los días de la semana.");
      }
    },

    quitarHorario(index) {
      this.nuevaActividad.horario.splice(index, 1);
    },

    async guardarActividad() {
      // VALIDACIÓN CAPACIDAD MÍNIMA
      if (this.nuevaActividad.capacidad_maxima < 1) {
        alert("La capacidad debe ser al menos de 1 persona.");
        return;
      }
      // VALIDACIÓN FECHA MÍNIMA
      if (this.nuevaActividad.horario.length === 0) {
        alert("Debes añadir al menos un horario para la plantilla.");
        return;
      }

      try {
        let url = '/actividades';
        let metodo = 'POST';

        if (this.editando) {
          url = `/actividades/${this.idActividadEditable}`;
          metodo = 'PUT';
        }

        await apiFetch(url, {
          method: metodo,
          body: JSON.stringify(this.nuevaActividad)
        });

        alert(this.editando ? "Actividad modificada" : "Actividad creada");
        this.cerrarLimpiarModal();
        await this.refrescarDashboard();

      } catch (err) {
        alert("Error al guardar: " + (err.ERROR || "Error desconocido"));
      }
    },

    async eliminarActividad(id) {
      const confirmacion = confirm("¿Estás seguro de que quieres eliminar esta actividad?");

      if (confirmacion) {
        try {
          await apiFetch(`/actividades/${id}`, {
            method: 'DELETE'
          });

          alert("Actividad eliminada con éxito.");
          await this.refrescarDashboard(); 

        } catch (err) {
          console.error("Error al eliminar:", err);
          alert("No se pudo eliminar la actividad: " + (err.ERROR || "Error del servidor"));
        }
      }
    },

    async cancelarSesion(idSesion) {
      if (confirm("¿Seguro que quieres anular esta sesión?")) {
        try {
          await apiFetch(`/sesiones/${idSesion}`, {
            method: 'DELETE'
          });

          alert("Sesión anulada.");
          await this.refrescarDashboard();

        } catch (err) {
          alert("Error al anular la sesión.");
        }
      }
    },

    async reservarSesion(idSesion) {
      // Buscamos la sesión en nuestro array local para validar antes de enviar
      const sesion = this.sesiones.find(s => s.id === idSesion);
      
      // Validación visual rápida
      if (sesion.capacidad_actual >= sesion.capacidad_maxima) {
        alert("Lo sentimos, esta clase ya está llena.");
        return;
      }

      try {
        // 3. Llamada al backend
        // En el body enviamos el id_sesion. El id_usuario lo sacará el backend del token/sesión.
        const res = await apiFetch('/reservas', {
          method: 'POST',
          body: JSON.stringify({ id_usuario: this.usuario.id, id_sesion: idSesion })
        });

        alert(res.mensaje || "¡Reserva realizada con éxito!.");
        await this.refrescarDashboard();

      } catch (err) {
        console.error("Error al reservar:", err);
        alert(err.ERROR || "No se pudo completar la reserva.");
      }
    },

    modificarActividad(actividad) {
      this.editando = true;
      this.idActividadEditable = actividad.id;
      
      // Clonamos los datos para no modificar la lista original por error
      this.nuevaActividad = JSON.parse(JSON.stringify(actividad));
      
      this.mostrarModalActividad = true;
    },

    // Ajustamos el botón de cerrar o cancelar para resetear el estado
    cerrarLimpiarModal() {
      this.mostrarModalActividad = false;
      this.editando = false;
      this.idActividadEditable = null;
      this.nuevaActividad = { nombre: '', descripcion: '', capacidad_maxima: 10, horario: [] };
    }
  }
}
</script>

<style scoped>
  @import "../styles/dashboard.css";
</style>