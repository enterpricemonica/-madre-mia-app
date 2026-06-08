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

// Mesa temporal. Más adelante (con el QR) vendrá del número de la URL.
const TABLE_ID = 1

function App() {
  const [menu, setMenu] = useState<MenuItem[]>([])

  // El carrito: un objeto que relaciona el id del item -> cantidad.
  // Ejemplo: { 2: 3, 4: 1 } = 3 arepas (id 2) y 1 bandeja (id 4).
  const [cart, setCart] = useState<Record<number, number>>({})

  // Traer el menú al cargar la pantalla
  useEffect(() => {
    fetch('http://localhost:8000/menu/')
      .then((response) => response.json())
      .then((data: MenuItem[]) => setMenu(data))
  }, [])

  // Agregar 1 unidad de un item al carrito
  function addToCart(itemId: number) {
    setCart((prev) => ({
      ...prev, // copiamos todo lo que ya estaba en el carrito
      [itemId]: (prev[itemId] || 0) + 1, // y le sumamos 1 a este item
    }))
  }

  // Calcular el total: recorremos el menú, y por cada item
  // multiplicamos su precio por la cantidad que haya en el carrito.
  let total = 0
  for (const item of menu) {
    const quantity = cart[item.id] || 0 // si no está en el carrito, 0
    total += item.price * quantity
  }

  // 🚀 TU MISIÓN: enviar el pedido al backend (POST /orders)
  function sendOrder() {
    const items = Object.entries(cart).map(([itemId, quantity]) => ({
      item_id: Number(itemId),
      quantity: Number(quantity),
    }))

    const payload = {
      table_id: TABLE_ID,
      items,
    }

    fetch('http://localhost:8000/orders/', {
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
    <div>
      <h1>Madre Mía 🫓</h1>

      {/* ── El menú ── */}
      <ul>
        {menu.map((item) => (
          <li key={item.id}>
            {item.name} — ${item.price.toLocaleString('es-CO')}{' '}
            <button onClick={() => addToCart(item.id)}>Agregar</button>
          </li>
        ))}
      </ul>

      {/* ── Tu pedido ── */}
      <h2>Tu pedido</h2>
      <ul>
        {menu
          .filter((item) => cart[item.id] > 0) // solo los que tienen cantidad
          .map((item) => (
            <li key={item.id}>
              {item.name} x {cart[item.id]}
            </li>
          ))}
      </ul>
      <p>
        <strong>Total: ${total.toLocaleString('es-CO')}</strong>
      </p>

      {/* El botón solo aparece si hay algo en el carrito (total > 0) */}
      {total > 0 && <button onClick={sendOrder}>Enviar pedido</button>}
    </div>
  )
}

export default App
