import { useState, useEffect } from 'react'
import './App.css'
import { useToast } from './Toast.tsx'
import { Confetti } from './Confetti.tsx'

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
  stock: number | null   // porciones restantes (null = ilimitado). M10 inventario
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
  const toast = useToast()
  const tableNumber = getTableNumberFromUrl()
  const [menu, setMenu] = useState<MenuItem[]>([])
  const [loading, setLoading] = useState(true) // true mientras carga el menú
  const [logoUrl, setLogoUrl] = useState('/logo.jpeg') // logo configurable desde el admin
  // Marca del negocio (configurable desde el admin → app reusable). Vacío hasta que carga.
  const [bizName, setBizName] = useState('')
  const [tagline, setTagline] = useState('')
  const [welcome, setWelcome] = useState('')

  // El carrito: un objeto que relaciona el id del item -> cantidad.
  // Ejemplo: { 2: 3, 4: 1 } = 3 arepas (id 2) y 1 bandeja (id 4).
  const [cart, setCart] = useState<Record<number, number>>({})

  // El id interno de la mesa (lo necesita el pedido). null = todavía no cargado.
  const [tableId, setTableId] = useState<number | null>(null)

  // Categoría activa (para resaltar el chip que se tocó)
  const [activeCat, setActiveCat] = useState('')

  // El último pedido creado, para ofrecer pagarlo. null = aún no se ha enviado.
  const [order, setOrder] = useState<{ id: number; total: number } | null>(null)

  // Propina (Ley 1935/2018: voluntaria, máx 10%). null = el cliente aún no elige
  // (NO se marca nada por defecto; la ley prohíbe agregarla sola). 'other' = monto a mano.
  const [tipChoice, setTipChoice] = useState<'none' | 'p5' | 'p10' | 'other' | null>(null)
  const [customTip, setCustomTip] = useState(0)

  // Estado del pago para la pantalla de confirmación:
  //   idle = sin pagar · waiting = esperando confirmación · approved/declined = resultado
  const [payState, setPayState] = useState<
    'idle' | 'waiting' | 'approved' | 'declined' | 'timeout'
  >('idle')

  // Cargar el script del Widget de Wompi una sola vez (solo el cliente lo necesita).
  useEffect(() => {
    const script = document.createElement('script')
    script.src = 'https://checkout.wompi.co/widget.js'
    script.async = true
    document.body.appendChild(script)
  }, [])

  // Traer el menú al cargar la pantalla
  useEffect(() => {
    fetch(`${API_URL}/menu/`)
      .then((response) => response.json())
      .then((data: MenuItem[]) => setMenu(data))
      .catch(() => {})
      .finally(() => setLoading(false)) // pase lo que pase, dejamos de "cargar"
  }, [])

  // Traer la marca configurada desde el admin (settings/theme): logo, nombre, eslogan, saludo
  useEffect(() => {
    fetch(`${API_URL}/settings/theme`)
      .then((r) => r.json())
      .then((s) => {
        if (s.logo_url) setLogoUrl(s.logo_url)
        if (s.tagline) setTagline(s.tagline)
        if (s.welcome) setWelcome(s.welcome)
        if (s.name) {
          setBizName(s.name)
          document.title = `${s.name} 🫓` // título de la pestaña, dinámico
        }
      })
      .catch(() => {})
  }, [])

  // Traducir el NÚMERO de la mesa (de la URL) a su ID interno,
  // usando el endpoint /tables/by-number que construiste.
  useEffect(() => {
    fetch(`${API_URL}/tables/by-number/${tableNumber}`)
      .then((response) => response.json())
      .then((table) => setTableId(table.id ?? null)) // si no existe, queda null
  }, [tableNumber])

  // Agregar 1 unidad de un item al carrito
  function addToCart(itemId: number) {
    const item = menu.find((m) => m.id === itemId)
    const current = cart[itemId] || 0
    // Inventario (M10): si el plato tiene stock limitado, no dejar pasar de lo disponible.
    if (item && item.stock !== null && current >= item.stock) {
      toast(item.stock <= 0 ? 'Agotado' : `Solo quedan ${item.stock}`, 'error')
      return
    }
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
      toast('No se reconoció la mesa. Revisa el código QR.', 'error')
      return
    }

    const items = Object.entries(cart).map(([itemId, quantity]) => ({
      item_id: Number(itemId),
      quantity: Number(quantity),
    }))

    const payload = {
      table_id: tableId, // 👈 el ID interno, no el número
      items,
    }

    fetch(`${API_URL}/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((newOrder) => {
        toast('¡Pedido enviado! #' + newOrder.id)
        setOrder({ id: newOrder.id, total }) // guardamos el total antes de vaciar
        setCart({})
      })
      .catch((error) => {
        console.error('Error al enviar el pedido:', error)
        toast('No se pudo enviar el pedido', 'error')
      })
  }

  // Pagar el pedido con Wompi (el cliente paga desde SU celular con el Widget).
  // Traduce la opción de propina a pesos. Topa en el 10% (tope legal) y usa floor
  // para no pasarnos del máximo que valida el backend (order.total // 10).
  function getTipAmount(): number {
    if (!order) return 0
    const maxTip = Math.floor(order.total * 0.1)
    if (tipChoice === 'p5') return Math.floor(order.total * 0.05)
    if (tipChoice === 'p10') return maxTip
    if (tipChoice === 'other') return Math.min(Math.max(customTip, 0), maxTip)
    return 0 // 'none' o aún sin elegir
  }

  function payWithWompi() {
    if (!order) return
    const orderId = order.id
    const tip = getTipAmount()

    // 1) Pedirle al backend el cobro YA FIRMADO (referencia + monto en centavos + firma).
    fetch(`${API_URL}/payments/wompi`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ order_id: orderId, tip_amount: tip }),
    })
      .then((r) => r.json())
      .then((data) => {
        // 2) Abrir el Widget. Mapear snake_case (backend) → camelCase (Wompi).
        //    OJO: la firma va ANIDADA en signature.integrity.
        const WidgetCheckout = (window as any).WidgetCheckout
        const checkout = new WidgetCheckout({
          currency: data.currency,
          amountInCents: data.amount_in_cents,
          reference: data.reference,
          publicKey: data.public_key,
          signature: { integrity: data.signature },
        })

        // 3) Cuando el cliente cierra el Widget, empezamos a esperar la confirmación.
        //    La verdad la pone el WEBHOOK en el backend → la consultamos con polling.
        checkout.open((result: any) => {
          const tx = result?.transaction
          if (tx?.status === 'APPROVED') {
            setPayState('waiting')
            pollPaymentStatus(orderId)
          } else {
            setPayState('declined')
          }
        })
      })
      .catch(() => toast('No se pudo iniciar el pago', 'error'))
  }

  // Preguntarle al backend si el pago ya quedó aprobado (lo confirma el webhook).
  // Reintenta cada 3s hasta ~1 minuto; si no, deja de insistir.
  function pollPaymentStatus(orderId: number, attempt = 0) {
    fetch(`${API_URL}/payments/${orderId}/status`)
      .then((r) => r.json())
      .then((p) => {
        if (p.status === 'approved') return setPayState('approved')
        if (p.status === 'declined') return setPayState('declined')
        // sigue pendiente → reintentar, o rendirse tras ~1 min
        if (attempt < 20) setTimeout(() => pollPaymentStatus(orderId, attempt + 1), 3000)
        else setPayState('timeout')
      })
      .catch(() => {
        if (attempt < 20) setTimeout(() => pollPaymentStatus(orderId, attempt + 1), 3000)
        else setPayState('timeout')
      })
  }

  // Volver a empezar tras un pago exitoso.
  function resetForNewOrder() {
    setOrder(null)
    setPayState('idle')
    setTipChoice(null)   // limpiar la propina para el siguiente pedido
    setCustomTip(0)
  }

  return (
    <div className="app">
      <header className="header">
        <img src={logoUrl} alt={tagline ? `${bizName} — ${tagline}` : bizName} className="header-logo" />
        <p className="welcome">{welcome}</p>
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
        {loading
          ? [...Array(5)].map((_, i) => (
              <div key={i} className="skel-card">
                <div className="skel-img" />
                <div className="skel-info">
                  <div className="skel-line skel-line-name" />
                  <div className="skel-line skel-line-desc" />
                  <div className="skel-line skel-line-price" />
                </div>
              </div>
            ))
          : categories.map((category) => (
          <section id={`cat-${slug(category)}`} key={category}>
            <h2 className="category-title">{category}</h2>
            {menu
              .filter((item) => item.category === category)
              .map((item) => {
                const soldOut = item.stock !== null && item.stock <= 0
                const reachedMax =
                  item.stock !== null && (cart[item.id] || 0) >= item.stock
                return (
                <article key={item.id} className={`card ${soldOut ? 'sold-out' : ''}`}>
                  {item.image_url && (
                    <img
                      src={item.image_url}
                      alt={`Foto de ${item.name}`}
                      className="card-img"
                    />
                  )}
                  <div className="card-info">
                    {item.featured && !soldOut && (
                      <span className="fav-badge">⭐ Favorito</span>
                    )}
                    {soldOut && <span className="soldout-badge">Agotado</span>}
                    {!soldOut && item.stock !== null && (
                      <span className="stock-left">Quedan {item.stock}</span>
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
                    disabled={soldOut || reachedMax}
                  >
                    {soldOut ? 'Agotado' : cart[item.id] ? `${cart[item.id]}  +` : '+'}
                  </button>
                </article>
                )
              })}
          </section>
        ))}
      </main>

      {/* Barra fija abajo: solo aparece si hay algo en el carrito */}
      {total > 0 && (
        <footer className="cart-bar">
          <div className="cart-bar-info">
            <span className="cart-count">
              {itemCount} {itemCount === 1 ? 'producto' : 'productos'}
            </span>
            <span className="cart-total" key={total}>
              ${total.toLocaleString('es-CO')}
            </span>
          </div>
          <button className="send-btn" onClick={sendOrder}>
            Enviar pedido
          </button>
        </footer>
      )}

      {/* Tras enviar el pedido (carrito vacío): elegir propina (voluntaria) y pagar con Wompi */}
      {order && total === 0 && (() => {
        const tip = getTipAmount()
        const totalToPay = order.total + tip
        const maxTip = Math.floor(order.total * 0.1)
        return (
        <footer className="cart-bar tip-bar">
          <div className="tip-section">
            <p className="tip-q">
              ¿Deseas dejar propina? <small>voluntaria, para el equipo 🙌</small>
            </p>
            <div className="tip-options">
              <button className={`tip-btn ${tipChoice === 'none' ? 'active' : ''}`} onClick={() => setTipChoice('none')}>No, gracias</button>
              <button className={`tip-btn ${tipChoice === 'p5' ? 'active' : ''}`} onClick={() => setTipChoice('p5')}>5%</button>
              <button className={`tip-btn ${tipChoice === 'p10' ? 'active' : ''}`} onClick={() => setTipChoice('p10')}>10%</button>
              <button className={`tip-btn ${tipChoice === 'other' ? 'active' : ''}`} onClick={() => setTipChoice('other')}>Otro</button>
            </div>
            {tipChoice === 'other' && (
              <div className="tip-custom">
                <span>$</span>
                <input
                  type="number"
                  min={0}
                  max={maxTip}
                  value={customTip || ''}
                  onChange={(e) => setCustomTip(Math.min(Math.max(parseInt(e.target.value) || 0, 0), maxTip))}
                  placeholder={`Máx $${maxTip.toLocaleString('es-CO')}`}
                />
                <small>máx ${maxTip.toLocaleString('es-CO')} (10%)</small>
              </div>
            )}
          </div>
          <div className="cart-bar-info">
            <span className="cart-count">Pedido #{order.id}</span>
            <div className="tip-breakdown">
              {tip > 0 && <span className="tip-line">+ propina ${tip.toLocaleString('es-CO')}</span>}
              <span className="cart-total">${totalToPay.toLocaleString('es-CO')}</span>
            </div>
          </div>
          <button className="send-btn" onClick={payWithWompi} disabled={tipChoice === null}>
            {tipChoice === null ? 'Elige propina ↑' : 'Pagar con Wompi'}
          </button>
        </footer>
        )
      })()}

      {/* Pantalla de confirmación del pago (se muestra encima de todo) */}
      {payState !== 'idle' && (
        <div className="pay-overlay">
          <div className="pay-card">
            {payState === 'waiting' && (
              <>
                <div className="pay-spinner" />
                <h2>Confirmando tu pago…</h2>
                <p>Un momento, estamos verificando con el banco.</p>
              </>
            )}
            {payState === 'approved' && (
              <>
                <Confetti />
                <div className="pay-icon pay-ok pay-ok-pop">✓</div>
                <h2>¡Pago confirmado!</h2>
                <p>Pedido #{order?.id} — ya está en cocina 🍳</p>
                <button className="send-btn" onClick={resetForNewOrder}>
                  Hacer otro pedido
                </button>
              </>
            )}
            {payState === 'declined' && (
              <>
                <div className="pay-icon pay-fail">✕</div>
                <h2>El pago no se completó</h2>
                <p>Puedes intentarlo de nuevo.</p>
                <button className="send-btn" onClick={() => setPayState('idle')}>
                  Reintentar
                </button>
              </>
            )}
            {payState === 'timeout' && (
              <>
                <div className="pay-icon pay-fail">⏳</div>
                <h2>Estamos confirmando tu pago</h2>
                <p>Está tardando más de lo normal. Si ya pagaste, avísale al personal.</p>
                <button className="send-btn" onClick={() => setPayState('idle')}>
                  Entendido
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default App
