import {
  createContext,
  useContext,
  useState,
  useCallback,
  type ReactNode,
} from 'react'
import './Toast.css'

type ToastType = 'success' | 'error'
interface ToastMsg {
  id: number
  text: string
  type: ToastType
}

// El "altavoz" compartido: una función para mostrar un mensajito desde cualquier pantalla.
const ToastContext = createContext<(text: string, type?: ToastType) => void>(
  () => {}
)

// Hook para usarlo fácil:  const toast = useToast();  toast('Guardado ✅')
export function useToast() {
  return useContext(ToastContext)
}

// El proveedor: envuelve toda la app, guarda los mensajes y los pinta arriba.
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMsg[]>([])

  const showToast = useCallback((text: string, type: ToastType = 'success') => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, text, type }])
    // Cada mensaje se borra solo a los 3 segundos.
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 3000)
  }, [])

  return (
    <ToastContext.Provider value={showToast}>
      {children}
      <div className="toast-container">
        {toasts.map((t) => (
          <div key={t.id} className={`toast toast-${t.type}`}>
            {t.text}
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}
