import { useState, useEffect } from 'react'
import './Admin.css'
import { useToast } from './Toast.tsx'
import { setFavicon } from './favicon.ts'

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
  stock: number | null   // porciones restantes (null = ilimitado). M10 inventario
}

const EMPTY_NEW = { name: '', description: '', price: 0, category: '', image_url: '', stock: '' }

// La forma del reporte de ventas (coincide con el backend)
interface SalesReport {
  date: string
  total: number        // total cobrado (ventas + propina)
  tips: number         // propina (a repartir al equipo)
  net_sales: number    // ventas del negocio, sin propina
  count: number
  by_method: Record<string, number>
}

// Nombres bonitos para cada método de pago
const METHOD_LABELS: Record<string, string> = {
  bre_b: 'Bre-B / QR',
  nequi: 'Nequi',
  daviplata: 'Daviplata',
  card: 'Tarjeta',
  efectivo: 'Efectivo',
  datafono: 'Datáfono',
  otro: 'Otro',
}

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
      <h1>🔑 Admin</h1>
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
  const toast = useToast()
  // El token vive en localStorage para no perderlo al recargar la página.
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('token')
  )
  const [items, setItems] = useState<MenuItem[]>([])
  const [newItem, setNewItem] = useState(EMPTY_NEW)
  const [theme, setTheme] = useState<Record<string, string> | null>(null)
  const [showTheme, setShowTheme] = useState(false) // panel de tema oculto por defecto
  const [boldEnabled, setBoldEnabled] = useState(false) // ¿el negocio cobra con Bold?
  const [showSettings, setShowSettings] = useState(false) // panel de configuración (⚙️)

  // Reportes de ventas
  const [showReports, setShowReports] = useState(false)
  const [report, setReport] = useState<SalesReport | null>(null)
  // Fecha local del dispositivo (en Colombia = fecha colombiana), formato YYYY-MM-DD.
  const [reportDate, setReportDate] = useState(() => {
    const d = new Date()
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const dd = String(d.getDate()).padStart(2, '0')
    return `${d.getFullYear()}-${mm}-${dd}`
  })

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
        .then((data) => {
          setTheme(data)
          setBoldEnabled(!!data.bold_enabled) // prendido/apagado del cobro Bold
          if (data.logo_url) setFavicon(data.logo_url)
          if (data.name) document.title = `Admin — ${data.name}`
        })
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
      body: JSON.stringify({ ...theme, bold_enabled: boldEnabled }),
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
        toast('Tema guardado ✅')
      })
      .catch(() => toast('No se pudo guardar el tema', 'error'))
  }

  // Prender/apagar el cobro con Bold y guardarlo de una (sin botón extra).
  function setBold(value: boolean) {
    if (!theme) return
    setBoldEnabled(value)
    fetch(`${API_URL}/settings/theme`, {
      method: 'PUT',
      headers: authHeaders,
      body: JSON.stringify({ ...theme, bold_enabled: value }),
    })
      .then((r) => {
        if (!r.ok) throw new Error('save failed')
        return r.json()
      })
      .then(() => toast(value ? 'Cobro con Bold activado 🤖' : 'Cobro con Bold desactivado'))
      .catch(() => toast('No se pudo guardar la configuración', 'error'))
  }

  // ── Reportes de ventas ──
  function loadReport(date: string) {
    fetch(`${API_URL}/reports/sales?date=${date}`, { headers: authHeaders })
      .then((r) => {
        if (!r.ok) throw new Error('report failed') // 401 si la sesión venció, etc.
        return r.json()
      })
      .then(setReport)
      .catch(() => {
        setReport(null) // no dejamos datos inválidos que rompan la pantalla
        toast('No se pudo cargar el reporte. ¿Sesión vencida? Sal y vuelve a entrar.', 'error')
      })
  }

  // Descargar el CSV. Como el endpoint está protegido, no sirve un <a href> normal
  // (no mandaría el token); lo bajamos con fetch + un link temporal.
  function downloadCsv() {
    fetch(`${API_URL}/reports/sales.csv?date=${reportDate}`, { headers: authHeaders })
      .then((r) => {
        if (!r.ok) throw new Error('csv failed')
        return r.blob()
      })
      .then((blob) => {
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `ventas-${reportDate}.csv`
        a.click()
        URL.revokeObjectURL(url)
      })
      .catch(() => toast('No se pudo descargar el CSV. ¿Sesión vencida? Sal y vuelve a entrar.', 'error'))
  }

  function changePrice(id: number, price: number) {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, price } : it)))
  }

  function changeImage(id: number, image_url: string) {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, image_url } : it)))
  }

  // Stock: vacío en pantalla = null (ilimitado); un número = porciones que quedan.
  function changeStock(id: number, stock: number | null) {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, stock } : it)))
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
      toast('El plato necesita al menos nombre y categoría', 'error')
      return
    }
    fetch(`${API_URL}/menu/`, {
      method: 'POST',
      headers: authHeaders,
      body: JSON.stringify({
        ...newItem,
        available: true,
        stock: newItem.stock === '' ? null : Number(newItem.stock), // vacío = ilimitado
      }),
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
        <h1>🧑‍🍳 Admin{theme?.name ? ` — ${theme.name}` : ''}</h1>
        <div className="admin-actions">
          <button
            className="icon-btn"
            onClick={() => {
              if (!showReports) loadReport(reportDate) // al abrir, carga el día de hoy
              setShowReports((s) => !s)
            }}
            title="Reportes de ventas"
          >
            📊
          </button>
          <button
            className="icon-btn"
            onClick={() => setShowTheme((s) => !s)}
            title="Tema (colores)"
          >
            🎨
          </button>
          <button
            className="icon-btn"
            onClick={() => setShowSettings((s) => !s)}
            title="Configuración"
          >
            ⚙️
          </button>
          <button className="logout" onClick={logout}>
            Salir
          </button>
        </div>
      </div>

      {/* ── Tema (colores) — se muestra solo al tocar el icono 🎨 ── */}
      {showTheme && theme && (
        <div className="theme-form">
          <h2>🎨 Marca, colores y logo</h2>

          {/* Marca del negocio — editable (app reusable / white-label) */}
          <label className="logo-field">
            <span>Nombre del negocio</span>
            <input
              type="text"
              value={theme.name || ''}
              onChange={(e) => setTheme((prev) => (prev ? { ...prev, name: e.target.value } : prev))}
              placeholder="Ej: Madre Mía"
            />
          </label>
          <label className="logo-field">
            <span>Eslogan</span>
            <input
              type="text"
              value={theme.tagline || ''}
              onChange={(e) => setTheme((prev) => (prev ? { ...prev, tagline: e.target.value } : prev))}
              placeholder="Ej: Arepas con Café de Origen"
            />
          </label>
          <label className="logo-field">
            <span>Saludo de bienvenida</span>
            <input
              type="text"
              value={theme.welcome || ''}
              onChange={(e) => setTheme((prev) => (prev ? { ...prev, welcome: e.target.value } : prev))}
              placeholder="Ej: Bienvenido 🫓"
            />
          </label>

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

          <label className="logo-field">
            <span>Logo (URL o ruta de la imagen)</span>
            <input
              type="text"
              value={theme.logo_url || ''}
              onChange={(e) =>
                setTheme((prev) => (prev ? { ...prev, logo_url: e.target.value } : prev))
              }
              placeholder="/logo.jpeg  o  https://..."
            />
          </label>
          {theme.logo_url && (
            <img src={theme.logo_url} alt="Vista previa del logo" className="logo-preview" />
          )}

          <button onClick={saveTheme}>Guardar tema</button>
        </div>
      )}

      {/* ── Configuración del negocio — se muestra al tocar ⚙️ ── */}
      {showSettings && theme && (
        <div className="theme-form">
          <h2>⚙️ Configuración</h2>
          <label className="bold-toggle">
            <input
              type="checkbox"
              checked={boldEnabled}
              onChange={(e) => setBold(e.target.checked)}
            />
            <span>🤖 Usar cobro con Bold (datáfono)</span>
          </label>
          <p className="settings-hint">
            Si está prendido, el botón “Datáfono” de la cocina cobra automáticamente con Bold.
            Si está apagado, solo marca el pago manualmente.
          </p>
        </div>
      )}

      {/* ── Reportes de ventas — se muestra al tocar 📊 ── */}
      {showReports && (
        <div className="report-panel">
          <h2>📊 Reporte de ventas</h2>
          <div className="report-controls">
            <label>
              Fecha:{' '}
              <input
                type="date"
                value={reportDate}
                onChange={(e) => {
                  setReportDate(e.target.value)
                  loadReport(e.target.value)
                }}
              />
            </label>
            <button onClick={downloadCsv}>⬇️ Descargar CSV</button>
          </div>

          {report && (
            <>
              <div className="report-summary">
                <p className="report-line">
                  Ventas netas:{' '}
                  <strong>${report.net_sales.toLocaleString('es-CO')}</strong>
                </p>
                <p className="report-line report-tips">
                  Propinas:{' '}
                  <strong>${report.tips.toLocaleString('es-CO')}</strong>
                </p>
                <p className="report-total">
                  Total cobrado:{' '}
                  <strong>${report.total.toLocaleString('es-CO')}</strong>{' '}
                  <span className="report-count">({report.count} pedidos)</span>
                </p>
              </div>
              <table className="report-table">
                <thead>
                  <tr>
                    <th>Método</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(report.by_method).map(([method, amount]) => (
                    <tr key={method}>
                      <td>{METHOD_LABELS[method] || method}</td>
                      <td>${amount.toLocaleString('es-CO')}</td>
                    </tr>
                  ))}
                  {report.count === 0 && (
                    <tr>
                      <td colSpan={2}>Sin ventas este día.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </>
          )}
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
        <input
          type="number"
          min={0}
          placeholder="Stock (vacío = ilimitado)"
          value={newItem.stock}
          onChange={(e) => setNewItem({ ...newItem, stock: e.target.value })}
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
            <th>Stock</th>
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
              <td className="stock-cell">
                <input
                  type="number"
                  min={0}
                  className="stock-input"
                  value={item.stock ?? ''}
                  placeholder="∞"
                  onChange={(e) =>
                    changeStock(item.id, e.target.value === '' ? null : Number(e.target.value))
                  }
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
