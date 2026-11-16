import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite' // 👈 Añadir esto

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(), // 👈 Añadir esto en los plugins
  ],
})