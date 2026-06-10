import { useState, useEffect } from 'react'
import './Admin.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface MenuItem {
  id: number
  name: string
  description: string | null
  price: number
  category: string
  available: boolean
}

const EMPTY_NEW = { name: '', description: '', price: 0, category: '' }

// ── Pantalla de login ──
// Recibe una función onLogin que se llama con el token cuando el login es exitoso.
function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  function submit() {
    fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
      .then((r) => {
        if (!r.ok) throw new Error('login failed')
        return r.json()
      })
      .then((data) => onLogin(data.access_token))
      .catch(() => setError('Usuario o contraseña incorrectos'))
  }

  return (
    <div className="login">
      <h1>🔑 Admin — Madre Mía</h1>
      <input
        placeholder="Usuario"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <input
        type="password"
        placeholder="Contraseña"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="login-error">{error}</p>}
      <button onClick={submit}>Entrar</button>
    </div>
  )
}

function Admin() {
  // El token vive en localStorage para no perderlo al recargar la página.
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('token')
  )
  const [items, setItems] = useState<MenuItem[]>([])
  const [newItem, setNewItem] = useState(EMPTY_NEW)

  // Headers con el token, para las acciones protegidas
  const authHeaders = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${token}`,
  }

  function logout() {
    localStorage.removeItem('token')
    setToken(null)
  }

  function loadItems() {
    fetch(`${API_URL}/menu/?available_only=false`)
      .then((r) => r.json())
      .then((data: MenuItem[]) => setItems(data))
  }
  useEffect(() => {
    if (token) loadItems()
  }, [token])

  function changePrice(id: number, price: number) {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, price } : it)))
  }

  function saveItem(item: MenuItem) {
    fetch(`${API_URL}/menu/${item.id}`, {
      method: 'PUT',
      headers: authHeaders,
      body: JSON.stringify(item),
    }).then(() => loadItems())
  }

  function toggleAvailable(item: MenuItem) {
    saveItem({ ...item, available: !item.available })
  }

  function deleteItem(id: number) {
    if (!confirm('¿Seguro que quieres borrar este plato?')) return
    fetch(`${API_URL}/menu/${id}`, {
      method: 'DELETE',
      headers: authHeaders,
    }).then(() => loadItems())
  }

  function addItem() {
    if (!newItem.name || !newItem.category) {
      alert('El plato necesita al menos nombre y categoría')
      return
    }
    fetch(`${API_URL}/menu/`, {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify({ ...newItem, available: true }),
    }).then(() => {
      setNewItem(EMPTY_NEW)
      loadItems()
    })
  }

  // Si no hay token, mostramos el login (y al entrar, guardamos el token)
  if (!token) {
    return (
      <Login
        onLogin={(t) => {
          localStorage.setItem('token', t)
          setToken(t)
        }}
      />
    )
  }

  return (
    <div className="admin">
      <div className="admin-top">
        <h1>🧑‍🍳 Admin — Madre Mía</h1>
        <button className="logout" onClick={logout}>
          Salir
        </button>
      </div>

      {/* ── Agregar plato ── */}
      <div className="add-form">
        <h2>Agregar plato</h2>
        <input
          placeholder="Nombre"
          value={newItem.name}
          onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
        />
        <input
          placeholder="Descripción"
          value={newItem.description}
          onChange={(e) => setNewItem({ ...newItem, description: e.target.value })}
        />
        <input
          type="number"
          placeholder="Precio"
          value={newItem.price || ''}
          onChange={(e) => setNewItem({ ...newItem, price: Number(e.target.value) })}
        />
        <input
          placeholder="Categoría"
          value={newItem.category}
          onChange={(e) => setNewItem({ ...newItem, category: e.target.value })}
        />
        <button onClick={addItem}>Agregar</button>
      </div>

      {/* ── Lista de platos ── */}
      <table className="items">
        <thead>
          <tr>
            <th>Plato</th>
            <th>Categoría</th>
            <th>Precio</th>
            <th>Estado</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id} className={item.available ? '' : 'hidden-item'}>
              <td>{item.name}</td>
              <td>{item.category}</td>
              <td className="price-cell">
                <input
                  type="number"
                  value={item.price}
                  onChange={(e) => changePrice(item.id, Number(e.target.value))}
                />
                <button onClick={() => saveItem(item)}>Guardar</button>
              </td>
              <td>
                <button onClick={() => toggleAvailable(item)}>
                  {item.available ? '✅ Disponible' : '🚫 Oculto'}
                </button>
              </td>
              <td>
                <button className="del" onClick={() => deleteItem(item.id)}>
                  Borrar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Admin
