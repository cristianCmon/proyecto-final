<template>
  <div class="dashboard-wrapper">
    <aside class="sidebar">
      <div class="sidebar-header">
        <img src="../assets/mancuerna.png" alt="Logo" class="mini-logo">
        <h3>GYM EX</h3>
      </div>
      <nav class="menu">
        <!-- IMPORTANTE click.prevent PARA QUE EL ENRUTADOR NO ACTUALICE Y LLEVE A VISTA LOGIN -->
        <!-- TAB ACTIVIDADES -->
        <a href="#" @click.prevent="tabActivo = 'actividades'" :class="['menu-item', { active: tabActivo === 'actividades' }]">
          <i>🏋️</i> Actividades
        </a>
        <!-- TAB SESIONES -->
        <a href="#" @click.prevent="tabActivo = 'sesiones'" :class="['menu-item', { active: tabActivo === 'sesiones' }]">
          <i>📅</i> Sesiones
        </a>
        <!-- TAB RESERVAS CLIENTE -->
        <div v-if="usuario.rol === 'cliente'" class="client-section">
          <a href="#" @click.prevent="tabActivo = 'reservasUsuario'" :class="['menu-item', { active: tabActivo === 'reservasUsuario' }]">
            <i>📋</i> Mis Reservas
          </a>
        </div>
        <div v-if="usuario.rol === 'administrador'" class="admin-section">
          <!-- TAB RESERVAS TOTALES (ADMIN) -->
          <a href="#" @click.prevent="tabActivo = 'reservasTotales'" :class="['menu-item', { active: tabActivo === 'reservasTotales' }]">
            <i>📋</i> Reservas
          </a>
          <!-- TAB ASISTENCIAS (ADMIN) -->
          <a href="#" @click.prevent="tabActivo = 'asistencias'" :class="['menu-item', { active: tabActivo === 'asistencias' }]">
            <i>✅</i> Asistencias
          </a>
        </div>
      </nav>
      <button @click="cerrarSesion" class="btn-logout">Cerrar Sesión</button>
    </aside>

    <main class="main-content">
      <header class="top-bar">
        <div class="page-info">
          <h2>{{ nombreTab }}</h2>
          <p>Bienvenido, <strong>{{ usuario.nombre_usuario }}</strong></p>
        </div>
        <div class="user-badge" :class="usuario.rol">{{ usuario.rol }}</div>
      </header>

      <section class="scrollable-area">

        <!-- CONTENIDO TAB ACTIVIDADES -->
        <div v-if="tabActivo === 'actividades'" class="tab-content">
          <div class="content-card">
            <div class="header-section">
              <h3>Oferta Actual</h3>
              <!-- FORZAMOS VARIABLE editando A FALSE PARA CONTROLAR CREAR/MODIFICAR -->
              <button v-if="usuario.rol === 'administrador'" @click="editando = false; mostrarModalActividad = true" class="btn-add">+ Nueva Actividad</button>
            </div>

            <div v-if="cargando" class="loader">Cargando catálogo...</div>

            <div v-else class="actividades-grid">
              <div v-for="act in actividades" :key="act.id" class="act-card">
                <div class="act-info">
                  <h4>{{ act.nombre }}</h4>
                  <p class="descripcion">{{ act.descripcion }}</p>
                  <!-- <div class="meta">
                    <span>👥 {{ act.capacidad_maxima }} plazas</span>
                  </div> -->
                </div>
                
                <div v-if="usuario.rol === 'administrador'" class="act-actions">
                  <div class="admin-controls-container">
                    <button @click="generarSesiones(act.id)" class="btn-generate">
                      Generar Sesiones
                    </button>
                    <button @click="modificarActividad(act)" class="btn-edit">Modificar</button>
                    <button @click="eliminarActividad(act.id)" class="btn-delete">Borrar</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- CONTENIDO TAB SESIONES -->
        <div v-if="tabActivo === 'sesiones'" class="tab-content">
          <div class="content-card">
            <div class="header-section">
              <h3>Próximas Sesiones</h3>
              <p v-if="usuario.rol === 'cliente'">Reserva tu plaza en las clases disponibles</p>
            </div>

            <div v-if="sesiones.length === 0" class="empty-state">
              <p>No hay sesiones programadas.</p>
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

        <!-- CONTENIDO TAB RESERVAS USUARIO -->
        <div v-if="tabActivo === 'reservasUsuario'" class="tab-content">
          <div class="content-card">
            <h3>Reservas Actuales</h3>
            <div v-if="reservasUsuario.length === 0" class="empty-state">
              <p>Aún no te has apuntado a ninguna actividad.</p>
            </div>
            
            <div v-else class="sesiones-table-container">
              <table class="sesiones-table">
                <thead>
                  <tr>
                    <th>Actividad</th>
                    <th>Fecha</th>
                    <th>Horario</th>
                    <th>Acción</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="reserva in reservasUsuario" :key="reserva.id_reserva">
                    <td><strong>{{ reserva.actividad }}</strong></td>
                    <td>{{ formatearFecha(reserva.fecha) }}</td>
                    <td>{{ reserva.hora_inicio }} - {{ reserva.hora_fin }}</td>
                    <td>
                      <button @click="cancelarReserva(reserva.id_reserva)" class="btn-delete-small">
                        Anular Reserva
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- CONTENIDO TAB LISTADO TOTAL RESERVAS (ADMINISTRADOR) -->
        <div v-if="tabActivo === 'reservasTotales' && usuario.rol === 'administrador'" class="tab-content">
          <div class="content-card">
            <div class="header-section">
              <h3>Listado Reservas Totales</h3>
            </div>

            <div v-if="listadoTotalReservas.length === 0" class="empty-state">
              <p>No hay registros de reservas.</p>
            </div>

            <div v-else class="sesiones-table-container">
              <table class="sesiones-table">
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Actividad</th>
                    <th>Fecha y Hora</th>
                    <th>Estado</th>
                    <!-- <th>Acciones</th> -->
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="res in listadoTotalReservas" :key="res.id_reserva">
                    <td><strong>{{ res.nombre_usuario }}</strong></td>
                    <td>{{ res.actividad }}</td>
                    <td>
                      <div class="fecha-celda">
                        <span>{{ formatearFecha(res.fecha) }} / {{ res.hora_inicio }} - {{ res.hora_fin }}</span>
                      </div>
                    </td>
                    <td>
                      <span :class="['status-pill', res.estado.toLowerCase()]">
                        {{ res.estado }}
                      </span>
                    </td>
                    <!-- <td>
                      <button @click="eliminarReserva(res.id_reserva)" class="btn-delete-small">
                        Eliminar
                      </button>
                    </td> -->
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- CONTENIDO TAB LISTADO ASISTENCIAS (ADMINISTRADOR) -->
        <div v-if="tabActivo === 'asistencias' && usuario.rol === 'administrador'" class="tab-content">
          <div class="content-card">
            <div class="header-section">
              <h3>Registro de Asistencia</h3>
            </div>

            <div v-if="asistencias.length === 0" class="empty-state">
              <p>No hay registros de asistencia.</p>
            </div>

            <div v-else class="sesiones-table-container">
              <table class="sesiones-table">
                <thead>
                  <tr>
                    <th>Alumno</th>
                    <th>Actividad / Sesión</th>
                    <th>Estado Actual</th>
                    <th>Cambiar Estado</th>
                  </tr>
                </thead>

                <tbody>
                  <tr v-for="asis in asistencias" :key="asis.id">
                    <td><strong>{{ asis.nombre_usuario }}</strong></td>
                    <td>
                      <div class="fecha-celda">
                        <span>{{ asis.actividad }} / {{ formatearFecha(asis.fecha) }}</span>
                      </div>
                    </td>
                    <td>
                      <span :class="['status-pill', asis.estado.replace(' ', '-').toLowerCase()]">
                        {{ asis.estado }}
                      </span>
                    </td>
                    <td>
                      <select 
                        :value="asis.estado" 
                        @change="estadoAsistencia(asis.id, $event.target.value)"
                        class="select-estado"
                      >
                        <option value="Pendiente">Pendiente</option>
                        <option value="Presente">Presente</option>
                        <option value="No presente">No presente</option>
                      </select>
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

<!-- LÓGICA -->
<script src="./Dashboard.js"></script>

<!-- ESTILOS -->
<style scoped>
  @import "../styles/dashboard.css";
</style>