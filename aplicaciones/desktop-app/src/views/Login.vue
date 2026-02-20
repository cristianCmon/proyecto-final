<template>
  <div class="login-container">
    <h2>Iniciar Sesión</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="usuario" type="text" placeholder="Usuario" required>
      <input v-model="password" type="password" placeholder="Contraseña" required>
      <button type="submit">Entrar</button>
    </form>
    <p v-if="error" style="color: red">{{ error }}</p>
  </div>
</template>

<script>
import api from '../api';

export default {
  data() {
    return {
      usuario: '',
      password: '',
      error: null
    }
  },
  methods: {
    async handleLogin() {
      try {
        const response = await api.post('/auth/login', {
          nombre_usuario: this.usuario,
          contraseña: this.password
        });
        
        // Guardamos el token que genera tu Flask
        localStorage.setItem('user-token', response.data.token);
        // Redirigir a la vista principal
        this.$router.push('/dashboard');
      } catch (err) {
        this.error = err.response?.data?.ERROR || "Error al conectar con el servidor";
      }
    }
  }
}
</script>