import { useState, useEffect } from 'react'
import './Kitchen.css'
import { useToast } from './Toast.tsx'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// La forma de un pedido y sus items (coincide con el backend)
interface OrderItem {
  id: number
  item_id: number
  name: string | null
  quantity: number
  notes: string | null
}
interface Order {
  id: number
  table_id: number
  status: string
  order_type: string
  is_paid: boolean
  total: number
  created_at: string
  items: OrderItem[]
}

// Para cada estado: cuál es el siguiente y qué texto va en el botón.
const NEXT_STATUS: Record<string, { next: string; label: string }> = {
  received: { next: 'preparing', label: 'Empezar a preparar' },
  preparing: { next: 'ready', label: 'Marcar listo' },
  ready: { next: 'delivered', label: 'Marcar entregado' },
}

// Métodos de pago manuales que la cocina puede marcar (el cliente paga por su cuenta).
type ManualMethod = 'efectivo' | 'datafono' | 'nequi' | 'daviplata' | 'bre_b'
const MANUAL_METHODS: { key: ManualMethod; label: string }[] = [
  { key: 'efectivo', label: '💵 Efectivo' },
  { key: 'datafono', label: '💳 Datáfono' },
  { key: 'nequi', label: '💜 Nequi' },
  { key: 'daviplata', label: '💙 Daviplata' },
  { key: 'bre_b', label: '📲 Bre-B' },
]

function Kitchen() {
  const toast = useToast()
  const [orders, setOrders] = useState<Order[]>([])
  const [boldEnabled, setBoldEnabled] = useState(false) // ¿el negocio cobra con Bold?
  const [bizName, setBizName] = useState('') // nombre del negocio (white-label)
  const [charging, setCharging] = useState<Set<number>>(new Set()) // pedidos cobrándose ahora

  // Pide los pedidos al backend
  function loadOrders() {
    fetch(`${API_URL}/orders/`)
      .then((r) => r.json())
      .then((data: Order[]) => {
        setOrders(data)
        // Si un pedido ya quedó pagado, ya no está "cobrando".
        setCharging((prev) => {
          const next = new Set(prev)
          for (const o of data) if (o.is_paid) next.delete(o.id)
          return next
        })
      })
  }

  // Al cargar: trae los pedidos YA, y luego repite cada 5 segundos (polling).
  useEffect(() => {
    loadOrders()
    const interval = setInterval(loadOrders, 5000)
    return () => clearInterval(interval) // limpiar el intervalo al salir
  }, [])

  // ¿Este negocio tiene activado el cobro con Bold? (lo decide el switch del admin)
  useEffect(() => {
    fetch(`${API_URL}/settings/theme`)
      .then((r) => r.json())
      .then((s) => {
        setBoldEnabled(!!s.bold_enabled)
        if (s.name) setBizName(s.name)
      })
      .catch(() => {})
  }, [])

  // Avanzar el estado de un pedido y recargar
  function advance(orderId: number, nextStatus: string) {
    fetch(`${API_URL}/orders/${orderId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: nextStatus }),
    }).then(() => loadOrders())
  }

  // Registrar cómo pagó y recargar.
  function recordPayment(orderId: number, method: ManualMethod) {
    fetch(`${API_URL}/payments/manual`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId, method }),
    }).then(() => {
      toast('Pago registrado ✅')
      loadOrders()
    })
  }

  // Iniciar el cobro REAL con Bold (datáfono). El resultado llega por webhook → el polling lo refleja.
  function startBoldCharge(orderId: number) {
    setCharging((prev) => new Set(prev).add(orderId))
    toast('Cobrando en el datáfono… 💳')
    fetch(`${API_URL}/payments/bold`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId, payment_method: 'POS' }),
    })
      .then((r) => {
        if (!r.ok) throw new Error('bold failed')
      })
      .catch(() => {
        toast('No se pudo iniciar el cobro con Bold', 'error')
        setCharging((prev) => {
          const next = new Set(prev)
          next.delete(orderId)
          return next
        })
      })
    // Si Bold rechaza o no llega el pago, liberamos los botones tras 60s para reintentar.
    setTimeout(() => {
      setCharging((prev) => {
        const next = new Set(prev)
        next.delete(orderId)
        return next
      })
    }, 60000)
  }

  // Un pedido sale de la cocina solo cuando está ENTREGADO **y** PAGADO.
  // Así Rachel puede registrar el pago aunque lo paguen después de comer.
  const activeOrders = orders
    .filter((o) => !(o.status === 'delivered' && o.is_paid))
    .sort((a, b) => a.id - b.id)

  return (
    <div className="kitchen">
      <h1>🍳 Cocina{bizName ? ` — ${bizName}` : ''}</h1>

      {activeOrders.length === 0 && (
        <p className="empty">No hay pedidos pendientes</p>
      )}

      <div className="orders">
        {activeOrders.map((order) => (
          <div key={order.id} className={`order-card status-${order.status}`}>
            <div className="order-head">
              <strong>
                Pedido #{order.id} · Mesa {order.table_id}{' '}
                {order.order_type === 'takeaway' ? '🥡' : '🍽️'}
              </strong>
              <span className="badge">{order.status}</span>
            </div>
            <ul>
              {order.items.map((it) => (
                <li key={it.id}>
                  {it.quantity}× {it.name}
                  {it.notes && <em> ({it.notes})</em>}
                </li>
              ))}
            </ul>
            {NEXT_STATUS[order.status] && (
              <button
                onClick={() => advance(order.id, NEXT_STATUS[order.status].next)}
              >
                {NEXT_STATUS[order.status].label}
              </button>
            )}

            {/* ── Pago: si ya pagó, sello; si no, "¿Cómo pagó?" ── */}
            <div className="pay-row">
              {order.is_paid ? (
                <span className="paid-badge">💵 Pagado</span>
              ) : charging.has(order.id) ? (
                <span className="charging-badge">💳 Cobrando en el datáfono…</span>
              ) : (
                <>
                  <span className="pay-ask-label">¿Cómo pagó?</span>
                  {MANUAL_METHODS.map((m) => (
                    <button
                      key={m.key}
                      className="pay-btn"
                      onClick={() =>
                        m.key === 'datafono' && boldEnabled
                          ? startBoldCharge(order.id) // 🤖 cobro real con Bold
                          : recordPayment(order.id, m.key) // marca manual (como hoy)
                      }
                    >
                      {m.label}
                    </button>
                  ))}
                </>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default Kitchen
