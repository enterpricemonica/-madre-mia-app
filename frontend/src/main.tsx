import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Kitchen from './Kitchen.tsx'

// Ruteo simple: si la URL empieza con /cocina, mostramos la pantalla de cocina;
// si no, el menú del cliente.
const isKitchen = window.location.pathname.startsWith('/cocina')

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {isKitchen ? <Kitchen /> : <App />}
  </StrictMode>,
)

