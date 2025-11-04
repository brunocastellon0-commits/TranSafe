import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    host: '0.0.0.0',  // ✅ Permite conexiones desde fuera del contenedor
    port: 5173,        // ✅ Puerto del servidor de desarrollo
    strictPort: true,  // ✅ Falla si el puerto ya está en uso
    watch: {
      usePolling: true // ✅ Necesario para Docker en algunos sistemas
    }
  }
})