import { apiFetch } from '../api';
/* eslint-disable */

export default {
  data() {
    return {
      tabActivo: 'actividades',
      usuario: {
        id: sessionStorage.getItem('idUsuario'),
        nombre_usuario: sessionStorage.getItem('nombre_usuario') || 'Usuario',
        rol: sessionStorage.getItem('rol') || 'cliente'
      },
      actividades: [],
      sesiones: [],
      reservasUsuario: [],
      listadoTotalReservas: [],
      asistencias: [],
      cargando: true,

			// CONFIGURACIÓN FORMULARIO ACTIVIDADES
      dias: ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
      nuevaActividad: {
        nombre: '',
        descripcion: '',
        capacidad_maxima: 10,
        horario: []
      },

			// CONTROL MODAL
    	mostrarModalActividad: false,
      editando: false,
      idActividadEditable: null,
    }
  },

  computed: {
		// DEVUELVE EL TÍTULO SEGÚN LA PESTAÑA DE FORMA DINÁMICA
    nombreTab() {
      if (this.tabActivo === 'actividades') return 'Catálogo de Actividades';
      if (this.tabActivo === 'sesiones') return 'Sesiones Programadas';
      if (this.tabActivo === 'reservasUsuario') return 'Mi Agenda Personal';
      if (this.tabActivo === 'reservasTotales') return 'Administración de Reservas';
      if (this.tabActivo === 'asistencias') return 'Control de Asistencia';

      return '';
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
		// CARGA DE DATOS DESDE EL BACK AL INICIAR DASHBOARD Y EN LOS REFRESCOS
    async refrescarDashboard() {
      this.cargando = true;

      try {
        const [dataAct, dataSes] = await Promise.all([
          apiFetch('/actividades'),
          apiFetch('/sesiones')
        ]);

        this.actividades = dataAct;
        this.sesiones = dataSes;

        // CARGA RESERVAS ESPECÍFICAS DE CLIENTE
        if (this.usuario.rol === 'cliente') {
          this.reservasUsuario = await apiFetch(`/usuarios/${this.usuario.id}/reservas-activas`);
        }

        // CARGA LISTADO TOTAL DE RESERVAS Y ASISTENCIAS FORMATEADAS
        if (this.usuario.rol === 'administrador') {
          this.listadoTotalReservas = await apiFetch('/reservas/admin');
          this.asistencias = await apiFetch('/asistencias/admin');
        }

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

      } catch (err) {
        alert("Error: " + (err.ERROR || "No se pudo generar"));
      }
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

          // REFRESCO SILENCIOSO
          await this.refrescarDashboard();

        } catch (err) {
          alert("Error al anular la sesión.");
        }
      }
    },

		async reservarSesion(idSesion) {
      // BUSCAMOS SESIÓN PARA VALIDAR
      const sesion = this.sesiones.find(s => s.id === idSesion);
      
      if (sesion.capacidad_actual >= sesion.capacidad_maxima) {
        alert("Lo sentimos, esta clase ya está llena.");
        return;
      }

      try {
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

    async cancelarReserva(idReserva) {
      if (confirm("¿Quieres cancelarla? Si faltan menos de 15 minutos no se liberará la plaza.")) {
        try {
          const res = await apiFetch(`/reservas/${idReserva}`, { 
            method: 'PUT',
            body: JSON.stringify({ estado: 'Cancelada' }) 
          });

          alert(res.mensaje); 
          await this.refrescarDashboard();

        } catch (err) {
          alert("Error al procesar la cancelación: " + (err.ERROR || "Inténtelo de nuevo"));
        }
      }
    },

    async eliminarReserva(idReserva) {
      if (confirm("¿Estás seguro de eliminar esta reserva permanentemente? Se actualizará el cupo si estaba confirmada.")) {
        try {
          await apiFetch(`/reservas/${idReserva}`, { method: 'DELETE' });
          alert("Reserva eliminada.");
          await this.refrescarDashboard();

        } catch (err) {
          alert("No se pudo eliminar.");
        }
      }
    },

    async estadoAsistencia(idAsistencia, nuevoEstado) {
      try {
        await apiFetch(`/asistencias/${idAsistencia}`, {
          method: 'PUT',
          body: JSON.stringify({ estado: nuevoEstado })
        });

        // REFRESCO SILENCIONSO SIN ALERT
        await this.refrescarDashboard();

      } catch (err) {
        alert("Error al actualizar asistencia");
      }
    },


    formatearFecha(fechaStr) {
      const opciones = { weekday: 'long', day: 'numeric', month: 'long' };
      return new Date(fechaStr).toLocaleDateString('es-ES', opciones);
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

    modificarActividad(actividad) {
      this.editando = true;
      this.idActividadEditable = actividad.id;
      
      // HACEMOS COPIA DEL ORIGINAL
      this.nuevaActividad = JSON.parse(JSON.stringify(actividad));
      
      this.mostrarModalActividad = true;
    },

    // LIMPIAMOS PARA RESETEAR EL MODAL
    cerrarLimpiarModal() {
      this.mostrarModalActividad = false;
      this.editando = false;
      this.idActividadEditable = null;
      this.nuevaActividad = { nombre: '', descripcion: '', capacidad_maxima: 10, horario: [] };
    },

		cerrarSesion() {
      sessionStorage.clear();
      this.$router.push('/');
    }
  }
	
}
