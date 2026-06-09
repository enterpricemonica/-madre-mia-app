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
}

function getTableNumberFromUrl() {
  const match = window.location.pathname.match(/\/table\/(\d+)/)
  return match ? Number(match[1]) : 1
}

// URL base del backend. En local: localhost. En producción (Vercel):
// se define la variable VITE_API_URL con la URL real de Railway.
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function App() {
  const tableNumber = getTableNumberFromUrl()
  const [menu, setMenu] = useState<MenuItem[]>([])

  // El carrito: un objeto que relaciona el id del item -> cantidad.
  // Ejemplo: { 2: 3, 4: 1 } = 3 arepas (id 2) y 1 bandeja (id 4).
  const [cart, setCart] = useState<Record<number, number>>({})

  // El id interno de la mesa (lo necesita el pedido). null = todavía no cargado.
  const [tableId, setTableId] = useState<number | null>(null)

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
      items,
    }

    fetch(`${API_URL}/orders/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((order) => {
        alert('¡Pedido enviado! #' + order.id)
        setCart({})
      })
      .catch((error) => {
        console.error('Error al enviar el pedido:', error)
        alert('No se pudo enviar el pedido')
      })
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Madre Mía 🫓</h1>
        <p className="subtitle">Mesa {tableNumber}</p>
      </header>

      <main className="menu">
        {categories.map((category) => (
          <section key={category}>
            <h2 className="category-title">{category}</h2>
            {menu
              .filter((item) => item.category === category)
              .map((item) => (
                <article key={item.id} className="card">
                  <div className="card-info">
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
          <div className="cart-bar-info">
            <span className="cart-count">
              {itemCount} {itemCount === 1 ? 'producto' : 'productos'}
            </span>
            <span className="cart-total">${total.toLocaleString('es-CO')}</span>
          </div>
          <button className="send-btn" onClick={sendOrder}>
            Enviar pedido
          </button>
        </footer>
      )}
    </div>
  )
}

export default App
