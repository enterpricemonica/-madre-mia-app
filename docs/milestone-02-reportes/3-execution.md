# M2 — Reportes de ventas · 3. Execution

> Plan de construcción: features, waves, pruebas. Rigor basado en riesgo: **tests completos** en lo de plata (sumas del reporte, pago manual); más ligero en la UI.

## Features
- **F1 · Pago manual (backend):** `POST /payments/manual` (efectivo/datáfono) → crea un `Payment` approved.
- **F2 · Reporte (backend):** `GET /reports/sales` (JSON) + `GET /reports/sales.csv` (descarga), protegidos.
- **F3 · Vista en /admin:** sección de reportes (total + por método + fecha + descargar CSV).
- **F4 · "¿Cómo pagó?" en cocina:** botones al cerrar el pedido.

## Waves
### Wave 1 — Backend (con TDD) 💳📊
- `POST /payments/manual` (valida método, monto del servidor, evita duplicar pago).
- `GET /reports/sales?date=` → total, count, by_method (solo `approved`).
- `GET /reports/sales.csv?date=` → CSV.
- Proteger con login admin.
- **Pruebas (rigor alto):** sumas por método con datos mock (efectivo + app mezclados), día correcto, solo approved cuenta, pago manual no se duplica.
- **Cierre:** suite verde.

### Wave 2 — Vista en /admin 📈
- Sección "📊 Reportes": total del día, tabla por método, selector de fecha, botón "Descargar CSV".
- **Cierre:** UAT de Monica.

### Wave 3 — "¿Cómo pagó?" en cocina 🍽️
- En `Kitchen.tsx`, al cerrar el pedido: botones 💵/💳/📲. Llama a `POST /payments/manual`.
- **Cierre:** UAT de Monica (cuadre completo de punta a punta).

## Despliegue
- Los endpoints nuevos son **aditivos** (nadie los llama hasta que exista la UI) → seguros de subir.
- **Lección aprendida:** la UI (admin/cocina) se sube a producción **solo cuando esté completa y probada**, no a medias.

## Fuera de alcance
- Productos más vendidos, PDF → futuro.
