<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <img src="../assets/mancuerna.png" alt="Logo" class="logo">
        <h1>GYM EX APP</h1>
      </div>
      
      <router-view />

    </div>
  </div>
</template>

<style scoped>
.auth-wrapper {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}
.auth-card {
  background: white;
  padding: 2.5rem;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  width: 100%;
  max-width: 400px;
}
.auth-header {
  text-align: center;
  margin-bottom: 2rem;
}
.logo {
  width: 60px;
  margin-bottom: 10px;
}
h1 {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}
</style>