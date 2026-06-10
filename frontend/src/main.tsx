import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Kitchen from './Kitchen.tsx'
import Admin from './Admin.tsx'

// Ruteo simple según la URL:
//   /cocina  → pantalla de cocina
//   /admin   → panel de administración
//   resto    → menú del cliente
const path = window.location.pathname
let screen = <App />
if (path.startsWith('/cocina')) screen = <Kitchen />
else if (path.startsWith('/admin')) screen = <Admin />

createRoot(document.getElementById('root')!).render(
  <StrictMode>{screen}</StrictMode>,
)

