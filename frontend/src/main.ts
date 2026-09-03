import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import './style.css'
import App from './App.vue'
import { useTheme } from './composables/useTheme'

const { initializeTheme } = useTheme()
initializeTheme()

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')
