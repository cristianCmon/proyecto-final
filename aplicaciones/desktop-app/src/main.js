import { createApp } from 'vue'
import App from './App.vue'
import router from './router'; // IMPORTAMOS ROUTER PARA ENLAZAR VISTAS

const app = createApp(App);

app.use(router); // INDICAMOS CARGA DE ROUTER
app.mount('#app');