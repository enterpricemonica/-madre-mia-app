import { useState, useEffect } from 'react'
import './App.css'

// La forma de un item del menú (coincide con el backend)
interface MenuItem {
  id: number
  name: string
  description: string | null
  price: number
  category: string
  available: boolean
  image_url: string | null
  featured: boolean
}

// La forma de un pedido creado (coincide con OrderOut del backend)
interface Order {
  id: number
  table_id: number
  status: string
  order_type: 'dine_in' | 'takeaway'
  is_paid: boolean
  total: number
}

// La respuesta al iniciar un cobro (coincide con PaymentInitOut del backend)
interface PaymentInit {
  id: number
  order_id: number
  method: string | null
  amount: number
  status: string
  qr_url: string | null
}

function getTableNumberFromUrl() {
  const match = window.location.pathname.match(/\/table\/(\d+)/)
  return match ? Number(match[1]) : 1
}

// URL base del backend. En local: localhost. En producción (Vercel):
// se define la variable VITE_API_URL con la URL real de Railway.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Convierte "Bebidas Frías" en "Bebidas-Frías" para usarlo como id (sin espacios)
const slug = (s: string) => s.replace(/\s+/g, '-')

function App() {
  const tableNumber = getTableNumberFromUrl()
  const [menu, setMenu] = useState<MenuItem[]>([])

  // El carrito: un objeto que relaciona el id del item -> cantidad.
  // Ejemplo: { 2: 3, 4: 1 } = 3 arepas (id 2) y 1 bandeja (id 4).
  const [cart, setCart] = useState<Record<number, number>>({})

  // El id interno de la mesa (lo necesita el pedido). null = todavía no cargado.
  const [tableId, setTableId] = useState<number | null>(null)

  // Categoría activa (para resaltar el chip que se tocó)
  const [activeCat, setActiveCat] = useState('')

  // Tipo de pedido: comer aquí (dine_in) o para llevar (takeaway). Arranca en "aquí".
  const [orderType, setOrderType] = useState<'dine_in' | 'takeaway'>('dine_in')

  // El pedido ya creado. null = todavía en el menú; con valor = pasamos a pagar.
  const [order, setOrder] = useState<Order | null>(null)

  // El método de pago que el cliente elige (null = aún no elige).
  const [selectedMethod, setSelectedMethod] = useState<'bre_b' | 'nequi' | 'card' | null>(null)

  // El cobro ya iniciado (trae el QR). null = aún no se ha iniciado.
  const [payment, setPayment] = useState<PaymentInit | null>(null)

  // true mientras le pedimos el QR al backend (para no tocar dos veces).
  const [paying, setPaying] = useState(false)

  // true cuando el backend confirma que el pago fue aprobado.
  const [paid, setPaid] = useState(false)

  // Traer el menú al cargar la pantalla
  useEffect(() => {
    fetch(`${API_URL}/menu/`)
      .then((response) => response.json())
      .then((data: MenuItem[]) => setMenu(data))
  }, [])

  // Traducir el NÚMERO de la mesa (de la URL) a su ID interno,
  // usando el endpoint /tables/by-number que construiste.
  useEffect(() => {
    fetch(`${API_URL}/tables/by-number/${tableNumber}`)
      .then((response) => response.json())
      .then((table) => setTableId(table.id ?? null)) // si no existe, queda null
  }, [tableNumber])

  // POLLING: mientras haya un cobro en curso y aún no esté pagado,
  // preguntamos cada 3s "¿ya pagaron?". Cuando diga approved, marcamos pagado.
  useEffect(() => {
    if (!payment || paid) return // nada que vigilar

    const interval = setInterval(() => {
      fetch(`${API_URL}/payments/${payment.order_id}/status`)
        .then((response) => response.json())
        .then((p) => {
          if (p.status === 'approved') setPaid(true)
        })
        .catch((error) => console.error('Error consultando el pago:', error))
    }, 3000)

    return () => clearInterval(interval) // limpieza: detener el reloj al salir
  }, [payment, paid])

  // Agregar 1 unidad de un item al carrito
  function addToCart(itemId: number) {
    setCart((prev) => ({
      ...prev, // copiamos todo lo que ya estaba en el carrito
      [itemId]: (prev[itemId] || 0) + 1, // y le sumamos 1 a este item
    }))
  }

  // Calcular total y cantidad de items recorriendo el menú
  let total = 0
  let itemCount = 0
  for (const item of menu) {
    const quantity = cart[item.id] || 0
    total += item.price * quantity
    itemCount += quantity
  }

  // Lista de categorías únicas (Entradas, Platos fuertes, Bebidas...)
  // new Set() elimina los repetidos; el [...] lo vuelve lista de nuevo.
  const categories = [...new Set(menu.map((item) => item.category))]

  // Enviar el pedido al backend (POST /orders)
  function sendOrder() {
    // Si todavía no sabemos el id de la mesa (o el QR es inválido), no enviamos.
    if (tableId === null) {
      alert('No se reconoció la mesa. Revisa el código QR.')
      return
    }

    const items = Object.entries(cart).map(([itemId, quantity]) => ({
      item_id: Number(itemId),
      quantity: Number(quantity),
    }))

    const payload = {
      table_id: tableId, // 👈 el ID interno, no el número
      order_type: orderType, // 🍽️ aquí o 🥡 llevar
      items,
    }

    fetch(`${API_URL}/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((createdOrder: Order) => {
        setOrder(createdOrder) // 👈 guardar el pedido → aparece la pantalla de pago
        setCart({}) // vaciamos el carrito
      })
      .catch((error) => {
        console.error('Error al enviar el pedido:', error)
        alert('No se pudo enviar el pedido')
      })
  }

  // Iniciar el cobro con el método elegido (POST /payments) → trae el QR.
  function startPayment(method: 'bre_b' | 'nequi' | 'card') {
    if (!order) return
    setSelectedMethod(method)
    setPaying(true)

    fetch(`${API_URL}/payments/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: order.id, method }),
    })
      .then((response) => response.json())
      .then((createdPayment: PaymentInit) => {
        setPayment(createdPayment) // 👈 guardar el cobro (con su QR) → mostramos el QR
        setPaying(false)
      })
      .catch((error) => {
        console.error('Error al iniciar el pago:', error)
        alert('No se pudo iniciar el pago')
        setPaying(false)
      })
  }

  // Volver al inicio (menú limpio) después de pagar o cancelar.
  function resetAll() {
    setOrder(null)
    setPayment(null)
    setPaid(false)
    setSelectedMethod(null)
  }

  // ── PANTALLA DE ÉXITO ──
  // Si el pago fue aprobado, mostramos la confirmación final.
  if (order && paid) {
    return (
      <div className="app pay-screen">
        <main className="pay-body pay-success">
          <span className="success-emoji">🎉</span>
          <h1 className="success-title">¡Pago exitoso!</h1>
          <p className="success-label">Tu número de pedido es</p>
          <p className="success-order">#{order.id}</p>
          <p className="success-msg">
            {order.order_type === 'takeaway'
              ? 'Te avisamos cuando esté listo para llevar 🥡'
              : 'Ya puedes esperar en tu mesa 🫓'}
          </p>
          <button className="send-btn" onClick={resetAll}>
            Hacer otro pedido
          </button>
        </main>
      </div>
    )
  }

  // ── PANTALLA DE PAGO ──
  // Si ya hay un pedido creado, mostramos esta pantalla en vez del menú.
  if (order) {
    return (
      <div className="app pay-screen">
        <header className="header">
          <img src="/logo.jpeg" alt="Madre Mía" className="header-logo" />
        </header>

        <main className="pay-body">
          <p className="pay-confirm">✅ Pedido #{order.id} creado</p>
          <p className="pay-type">
            {order.order_type === 'takeaway' ? '🥡 Para llevar' : '🍽️ Para comer aquí'}
          </p>

          <p className="pay-total-label">Total a pagar</p>
          <p className="pay-total">${order.total.toLocaleString('es-CO')}</p>

          {!payment ? (
            // ── Momento 1: elegir cómo pagar ──
            <>
              <h2 className="pay-q">¿Cómo quieres pagar?</h2>
              <div className="pay-methods">
                <button
                  className={`pay-method ${selectedMethod === 'bre_b' ? 'active' : ''}`}
                  onClick={() => startPayment('bre_b')}
                  disabled={paying}
                >
                  📲 Bre-B / QR
                </button>
                <button
                  className={`pay-method ${selectedMethod === 'nequi' ? 'active' : ''}`}
                  onClick={() => startPayment('nequi')}
                  disabled={paying}
                >
                  💜 Nequi
                </button>
                <button
                  className={`pay-method ${selectedMethod === 'card' ? 'active' : ''}`}
                  onClick={() => startPayment('card')}
                  disabled={paying}
                >
                  💳 Tarjeta
                </button>
              </div>
              {paying && <p className="pay-waiting">Generando tu QR…</p>}

              <button
                className="pay-back"
                onClick={() => {
                  setOrder(null) // volvemos al menú
                  setSelectedMethod(null)
                }}
              >
                ← Volver al menú
              </button>
            </>
          ) : (
            // ── Momento 2: mostrar el QR y esperar el pago ──
            <>
              <div className="qr-box">
                <span className="qr-emoji">📲</span>
                <span className="qr-text">Escanea para pagar</span>
              </div>
              <p className="pay-waiting">⏳ Esperando tu pago…</p>
              <p className="qr-ref">Pago #{payment.id} · {payment.method}</p>

              <button
                className="pay-back"
                onClick={() => {
                  setPayment(null) // volver a elegir método
                  setSelectedMethod(null)
                }}
              >
                ← Elegir otro método
              </button>
            </>
          )}
        </main>
      </div>
    )
  }

  return (
    <div className="app">
      <header className="header">
        <img src="/logo.jpeg" alt="Madre Mía — Arepas con Café de Origen" className="header-logo" />
        <p className="welcome">Bienvenido 🫓</p>
        <p className="table-pill">Mesa {tableNumber}</p>
      </header>

      {/* Barra de categorías (chips) — salta a cada sección */}
      <nav className="cat-nav">
        {categories.map((cat) => (
          <button
            key={cat}
            className={`cat-chip ${activeCat === cat ? 'active' : ''}`}
            onClick={() => {
              setActiveCat(cat)
              document
                .getElementById(`cat-${slug(cat)}`)
                ?.scrollIntoView({ behavior: 'smooth', block: 'start' })
            }}
          >
            {cat}
          </button>
        ))}
      </nav>

      <main className="menu">
        {categories.map((category) => (
          <section id={`cat-${slug(category)}`} key={category}>
            <h2 className="category-title">{category}</h2>
            {menu
              .filter((item) => item.category === category)
              .map((item) => (
                <article key={item.id} className="card">
                  {item.image_url && (
                    <img
                      src={item.image_url}
                      alt={`Foto de ${item.name}`}
                      className="card-img"
                    />
                  )}
                  <div className="card-info">
                    {item.featured && (
                      <span className="fav-badge">⭐ Favorito</span>
                    )}
                    <h3 className="card-name">{item.name}</h3>
                    {item.description && (
                      <p className="card-desc">{item.description}</p>
                    )}
                    <p className="card-price">
                      ${item.price.toLocaleString('es-CO')}
                    </p>
                  </div>
                  <button
                    className="add-btn"
                    onClick={() => addToCart(item.id)}
                  >
                    {cart[item.id] ? `${cart[item.id]}  +` : '+'}
                  </button>
                </article>
              ))}
          </section>
        ))}
      </main>

      {/* Barra fija abajo: solo aparece si hay algo en el carrito */}
      {total > 0 && (
        <footer className="cart-bar">
          {/* Toggle: ¿comer aquí o para llevar? (mismo patrón que los chips de categoría) */}
          <div className="order-type">
            <button
              className={`type-chip ${orderType === 'dine_in' ? 'active' : ''}`}
              onClick={() => setOrderType('dine_in')}
            >
              🍽️ Aquí
            </button>
            <button
              className={`type-chip ${orderType === 'takeaway' ? 'active' : ''}`}
              onClick={() => setOrderType('takeaway')}
            >
              🥡 Llevar
            </button>
          </div>

          <div className="cart-bar-main">
            <div className="cart-bar-info">
              <span className="cart-count">
                {itemCount} {itemCount === 1 ? 'producto' : 'productos'}
              </span>
              <span className="cart-total">${total.toLocaleString('es-CO')}</span>
            </div>
            <button className="send-btn" onClick={sendOrder}>
              Enviar pedido
            </button>
          </div>
        </footer>
      )}
    </div>
  )
}

export default App
