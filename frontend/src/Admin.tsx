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
  image_url: string | null
  featured: boolean
}

const EMPTY_NEW = { name: '', description: '', price: 0, category: '', image_url: '' }

// Los 8 colores del tema (estilo Bootstrap) con su etiqueta
const THEME_FIELDS = [
  { key: 'primary', label: 'Principal' },
  { key: 'secondary', label: 'Secundario' },
  { key: 'success', label: 'Éxito' },
  { key: 'danger', label: 'Peligro' },
  { key: 'warning', label: 'Advertencia' },
  { key: 'info', label: 'Info' },
  { key: 'light', label: 'Fondo' },
  { key: 'dark', label: 'Texto' },
]

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
  const [theme, setTheme] = useState<Record<string, string> | null>(null)
  const [showTheme, setShowTheme] = useState(false) // panel de tema oculto por defecto

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
    if (token) {
      loadItems()
      fetch(`${API_URL}/settings/theme`)
        .then((r) => r.json())
        .then(setTheme)
    }
  }, [token])

  // Cambiar un color del tema: actualiza el estado Y lo aplica en vivo (preview)
  function changeThemeColor(key: string, value: string) {
    setTheme((prev) => (prev ? { ...prev, [key]: value } : prev))
    document.documentElement.style.setProperty(`--${key}`, value) // preview inmediato
  }

  // Guardar el tema y aplicarlo de inmediato a la pantalla
  function saveTheme() {
    if (!theme) return
    fetch(`${API_URL}/settings/theme`, {
      method: 'PUT',
      headers: authHeaders,
      body: JSON.stringify(theme),
    })
      .then((r) => {
        if (!r.ok) throw new Error('save failed')
        return r.json()
      })
      .then((saved: Record<string, string>) => {
        const root = document.documentElement
        for (const [name, value] of Object.entries(saved)) {
          root.style.setProperty(`--${name}`, value)
        }
        alert('Tema guardado ✅')
      })
      .catch(() => alert('No se pudo guardar el tema'))
  }

  function changePrice(id: number, price: number) {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, price } : it)))
  }

  function changeImage(id: number, image_url: string) {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, image_url } : it)))
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

  function toggleFeatured(item: MenuItem) {
    saveItem({ ...item, featured: !item.featured })
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
        <div className="admin-actions">
          <button
            className="icon-btn"
            onClick={() => setShowTheme((s) => !s)}
            title="Tema (colores)"
          >
            🎨
          </button>
          <button className="logout" onClick={logout}>
            Salir
          </button>
        </div>
      </div>

      {/* ── Tema (colores) — se muestra solo al tocar el icono 🎨 ── */}
      {showTheme && theme && (
        <div className="theme-form">
          <h2>🎨 Tema (colores)</h2>
          <div className="theme-grid">
            {THEME_FIELDS.map((f) => (
              <label key={f.key} className="theme-field">
                <span>{f.label}</span>
                <input
                  type="color"
                  value={theme[f.key]}
                  onChange={(e) => changeThemeColor(f.key, e.target.value)}
                />
              </label>
            ))}
          </div>
          <button onClick={saveTheme}>Guardar tema</button>
        </div>
      )}

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
        <input
          placeholder="Ruta de la foto (ej: /photos/arepa.jpg)"
          value={newItem.image_url}
          onChange={(e) => setNewItem({ ...newItem, image_url: e.target.value })}
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
            <th>Foto</th>
            <th>Estado</th>
            <th>⭐</th>
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
                <input
                  className="img-input"
                  value={item.image_url || ''}
                  onChange={(e) => changeImage(item.id, e.target.value)}
                  placeholder="/photos/..."
                />
              </td>
              <td>
                <button onClick={() => toggleAvailable(item)}>
                  {item.available ? '✅ Disponible' : '🚫 Oculto'}
                </button>
              </td>
              <td>
                <button onClick={() => toggleFeatured(item)} title="Favorito">
                  {item.featured ? '⭐' : '☆'}
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
