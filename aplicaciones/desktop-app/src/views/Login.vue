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
import { apiFetch } from '../api';

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
        const data = await apiFetch('/auth/login', {
          method: 'POST',
          body: JSON.stringify({
            nombre_usuario: this.usuario,
            contraseña: this.password // Tal cual lo espera tu Flask
          })
        });
        
        localStorage.setItem('user-token', data.token);
        this.$router.push('/dashboard');
      } catch (err) {
        // 'err' aquí es el JSON de error que envía tu Flask (p.ej. {"ERROR": "..."})
        this.error = err.ERROR || "Error en el servidor";
      }
    }
  }
}
</script>