# M2 — Reportes de ventas · 2. Research Plan

> Cómo lo construimos, técnicamente.

## Idea central: todo se unifica en `Payment`
El reporte = **agrupar los pagos `approved` de un día por método y sumar**. No hace falta un modelo nuevo.

- **Métodos de la app:** `bre_b`, `nequi`, `card` (provider `bold`, los confirma el webhook).
- **Métodos manuales:** `efectivo`, `datafono` (provider `manual`, los registra Rachel en cocina).

## Registrar un pago manual (efectivo/datáfono)
- Endpoint nuevo: `POST /payments/manual` con `{ order_id, method }` (method ∈ efectivo/datafono).
- Crea un `Payment(provider="manual", method, amount=order.total, status="approved")`.
- **Seguridad:** el monto sale del pedido (servidor), nunca del cliente.

## El reporte
- Endpoint: `GET /reports/sales?date=YYYY-MM-DD` (protegido con login admin, como el resto de `/admin`).
- Devuelve: `date`, `total`, `count`, y `by_method` (suma por cada método).
- **Base de tiempo:** se cuenta por `Payment.created_at` del día pedido (cuándo entró la plata). Solo cuenta `status="approved"`.
- **CSV:** `GET /reports/sales.csv?date=...` → archivo `text/csv` con una fila por método + el total. Se arma con el módulo `csv` de la librería estándar de Python.

## UI
- **`/admin`:** sección "📊 Reportes" → muestra el total del día + tabla por método + selector de fecha + botón **"Descargar CSV"**.
- **Cocina (`Kitchen.tsx`):** al cerrar un pedido, botones **"¿Cómo pagó?"** (💵 Efectivo · 💳 Datáfono · 📲 App). Los ya pagados por app salen marcados.

## Seguridad
- Los endpoints de reporte van **protegidos** (`Depends(get_current_user)`), igual que el CRUD del menú.
- Idempotencia/duplicados: evitar registrar dos pagos para el mismo pedido.

## Fuera de alcance (por ahora)
- Productos más vendidos y PDF → mejoras futuras (el cuadre va primero).
