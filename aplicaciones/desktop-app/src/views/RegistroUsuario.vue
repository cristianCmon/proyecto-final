<template>
  <div class="registro-container">
    <h2>Registro de Usuario</h2>
    <form @submit.prevent="handleRegistro">
      <input v-model="form.nombre_usuario" placeholder="Usuario" required>
      <input v-model="form.contraseña" type="password" placeholder="Contraseña" required>
      <input v-model="form.email" type="email" placeholder="Email" required>
      <input v-model="form.nombre" placeholder="Nombre">
      <input v-model="form.apellidos" placeholder="Apellidos">
      <input v-model="form.dni" placeholder="DNI" required>
      <input v-model="form.telefono" placeholder="Teléfono">
      
      <button type="submit">Registrarse</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script>
import { apiFetch } from '../api';

export default {
  data() {
    return {
      form: {
        nombre_usuario: '',
        contraseña: '',
        email: '',
        nombre: '',
        apellidos: '',
        dni: '',
        telefono: ''
      },
      error: null
    }
  },
  methods: {
    async handleRegistro() {
      try {
        await apiFetch('/auth/registro', {
          method: 'POST',
          body: JSON.stringify(this.form)
        });
        alert("¡Registro con éxito!");
        this.$router.push('/'); // Volver al login
      } catch (err) {
        this.error = err.ERROR || "Error al registrar";
      }
    }
  }
}
</script>