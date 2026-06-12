import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Kitchen from './Kitchen.tsx'
import Admin from './Admin.tsx'
import { ToastProvider } from './Toast.tsx'

// Aplica el tema (colores) guardado en el backend a TODA la app.
// Sobreescribe las variables CSS (--primary, etc.) que index.css usa.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
fetch(`${API_URL}/settings/theme`)
  .then((r) => r.json())
  .then((theme: Record<string, string>) => {
    const root = document.documentElement
    for (const [name, value] of Object.entries(theme)) {
      root.style.setProperty(`--${name}`, value)
    }
  })
  .catch(() => {})

// Ruteo simple según la URL:
//   /cocina  → pantalla de cocina
//   /admin   → panel de administración
//   resto    → menú del cliente
const path = window.location.pathname
let screen = <App />
if (path.startsWith('/cocina')) screen = <Kitchen />
else if (path.startsWith('/admin')) screen = <Admin />

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ToastProvider>{screen}</ToastProvider>
  </StrictMode>,
)

