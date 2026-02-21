<template>
  <div class="registro-container">
    <h2>Registro de Usuario</h2>
    <form @submit.prevent="validarRegistro">
      <input v-model="form.nombre" placeholder="Nombre" required>
      <input v-model="form.apellidos" placeholder="Apellidos" required>
      <input v-model="form.dni" placeholder="DNI" required>
      <input v-model="form.email" type="email" placeholder="Email" required>
      <input v-model="form.telefono" placeholder="Teléfono">
      <input v-model="form.nombre_usuario" placeholder="Nombre de usuario" required>
      <input v-model="form.contraseña" type="password" placeholder="Contraseña" required>
      
      <button type="submit">Registrarse</button>
    </form>
    <div class="auth-footer">
      <p>¿Ya tienes cuenta? 
        <router-link to="/">Inicia sesión</router-link>
      </p>
    </div>
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
    async validarRegistro() {
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