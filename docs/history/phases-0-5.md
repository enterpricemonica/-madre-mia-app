# Historial: Fases 0 a 5 (backfill)

Documentación retroactiva de lo ya construido y desplegado, con el *por qué* de cada decisión.

---

## Fase 0 — Limpieza y fundación
**Objetivo:** dejar la base sólida y segura antes de construir encima.
- Se sacaron `.env` y `__pycache__` del control de git y se agregó `.gitignore`. Se creó `.env.example` como plantilla segura.
- Se **rotó la contraseña de PostgreSQL** y la `SECRET_KEY` (estaban comprometidas en el historial de git).
- Se **migró todo el código de español a inglés** (`Mesa→Table`, `Pedido→Order`, etc.) para consistencia profesional, mientras el proyecto era pequeño.
- Se arregló un bug de import en `main.py`, se agregó `requirements.txt` y `seed.py` (carga del menú).
- **Lección:** los secretos nunca se commitean; si se filtran, se rotan.

## Fase 1 — Motor de pedidos (backend)
**Objetivo:** el corazón de la app. Todo lo demás es una vista de los pedidos.
- Router `orders.py`: `POST /orders` (crear), `GET /orders` (listar), `GET /orders/{id}`, `PATCH /orders/{id}/status`.
- **Decisión clave:** el `total` se calcula en el servidor leyendo el precio real de la BD; el cliente nunca manda precios. Evita que alguien manipule el cobro.
- Validación de estados contra una lista `VALID_STATUSES`. Transiciones libres a propósito (el personal puede corregir errores).

## Fase 2 — App del cliente por QR + Deploy
**Objetivo:** el "first win" — que el cliente pida desde su celular.
- Frontend React+TS+Vite: menú (`GET /menu`), carrito (`useState`), envío de pedido (`POST /orders`).
- Diseño **mobile-first** (cards por categoría, barra fija de carrito, paleta terracota).
- **Mesa desde el QR:** la URL `/table/N` trae el número; el endpoint `GET /tables/by-number/{n}` lo traduce al `id` interno (número ≠ id).
- **Deploy:** se subió a producción (Railway + Vercel). Se hicieron configurables las URLs (`VITE_API_URL`, `FRONTEND_URL`) y se agregó `vercel.json` para rutas SPA.
- **Lección de BD:** un plato con pedidos no se puede borrar (foreign key). `seed.py` se reescribió a **upsert + soft-delete**.

## Fase 3 — Pantalla de cocina
**Objetivo:** que la cocina vea y gestione los pedidos.
- Pantalla `/cocina` con **polling** (consulta cada 5 s con `setInterval`) — más simple que WebSockets y suficiente para el tamaño del negocio.
- Avanza el estado de cada pedido (`PATCH`). Franja de color por estado, FIFO (más viejo primero).
- Backend: se agregó el **nombre del plato** a cada `OrderItem` (propiedad en el modelo) para que la cocina vea "Vegetariana", no "item 14".

## Fase 5 — Panel de admin + Login
**Objetivo:** que la dueña administre el menú sin tocar código, de forma segura.
- `GET /menu` ahora acepta `available_only` (el admin ve también los ocultos).
- Pantalla `/admin`: CRUD de menú (editar precio, activar/ocultar, agregar, borrar).
- **Autenticación:** hash de contraseñas con PBKDF2 (stdlib, sin dependencias que compilen en Python 3.14), tokens **JWT** (PyJWT) firmados con `SECRET_KEY`. Endpoints de escritura del menú protegidos con `Depends(get_current_user)`; los de lectura quedan públicos.
- El usuario admin se crea al arrancar desde variables de entorno (`ADMIN_USERNAME`, `ADMIN_PASSWORD`). El token se guarda en `localStorage`.

---

## Pendiente / deuda técnica conocida
- 🔒 **CORS** abierto a `*` — debe cerrarse al dominio de Vercel.
- ⏳ Expiración del token (12 h) sin manejo explícito en el frontend.
- 🎨 UX por modernizar (Fase 7).
- 📱 Tablet del mesero (Fase 4).
- 💳 Pagos (Fase 6 — en discusión).
