# Madre Mía — Visión general del proyecto

> Documento maestro. Si alguien llega nuevo al proyecto, empieza por aquí.

## ¿Qué es Madre Mía?
Aplicación de pedidos para un restaurante de **arepas ocañeras** en Colombia. Permite:
- Que el **cliente** escanee un QR en su mesa, vea el menú y haga el pedido desde su celular.
- Que la **cocina** vea los pedidos entrando en vivo y los gestione.
- Que la **dueña (admin)** administre el menú y los precios con login.

El restaurante usa **BOLD** como POS (datáfono) y recibe pagos por Nequi, Daviplata, datáfono BOLD y llave Bre-B.

## Arquitectura (3 capas)
```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   FRONTEND    │ ──> │    BACKEND    │ ──> │ BASE DE DATOS │
│ React+TS+Vite │     │    FastAPI    │     │  PostgreSQL   │
│   (Vercel)    │     │   (Railway)   │     │   (Railway)   │
└───────────────┘     └───────────────┘     └───────────────┘
```

## Pantallas (surfaces)
| Ruta | Quién la usa | Estado |
|------|--------------|--------|
| `/table/:n` | Cliente (escanea QR) | ✅ en producción |
| `/cocina` | Cocina | ✅ en producción |
| `/admin` | Dueña (con login) | ✅ en producción |
| Tablet del mesero | Meseros | ⬜ Fase 4 (pendiente) |

## URLs de producción
- Frontend: https://madre-mia-app.vercel.app
- Backend: https://madre-mia-app-production.up.railway.app

## Stack técnico
- **Backend:** Python 3.14, FastAPI, SQLAlchemy, PostgreSQL. Auth con JWT (PyJWT) + hash PBKDF2.
- **Frontend:** React 19 + TypeScript + Vite. Sin framework de UI (CSS propio).
- **Infra:** Railway (backend + DB), Vercel (frontend), GitHub (código + auto-deploy).
- **Convención:** conversación en español, **código e identificadores en inglés**.

## Modelo de datos (resumen)
- `MenuItem` — platos (name, description, price COP, category, available)
- `Table` — mesas (number, qr_code, active). Ojo: `number` (visible) ≠ `id` (interno).
- `Order` — pedidos (table_id, status, total, created_at)
- `OrderItem` — líneas del pedido (order_id, item_id, quantity, notes)
- `User` — usuarios admin (username, hashed_password)

Estados del pedido: `received → preparing → ready → delivered → paid`

## Decisiones de diseño importantes
- **El total SIEMPRE se calcula en el servidor** leyendo precios de la BD, nunca se confía en el cliente. (Seguridad anti-manipulación.)
- **Precios en enteros (COP)** — el peso colombiano no tiene decimales.
- **Soft-delete del menú:** un plato que ya tiene pedidos no se borra; se marca `available=False`. Protege la integridad referencial (foreign keys).

Ver el historial detallado en [history/phases-0-5.md](history/phases-0-5.md) y cómo trabajamos en [methodology.md](methodology.md).
