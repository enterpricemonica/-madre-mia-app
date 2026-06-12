# M1 · Integración Bold REAL · 3. Execution

> Waves. Rigor alto (es plata): tests con mocks, webhook idempotente, validaciones.

## Wave 1 — Mock server de Bold 🤖 (Python/FastAPI)
- App aparte (`mock-bold/`, puerto 9000) con los 3 endpoints:
  - `GET /payments/payment-methods`, `GET /payments/binded-terminals`, `POST /payments/app-checkout`.
- Auth: exige header `Authorization: x-api-key ...`.
- `app-checkout`: valida el body (AP002–AP006), responde **201 + integration_id**, y **dispara el webhook** a la tienda ~unos segundos después según los **montos mágicos**.
- **Cierre:** probar los 3 endpoints + que el webhook llegue.

## Wave 2 — Adapter de Bold en el backend 💳
- `bold_gateway.py`: arma el body (amount, `reference` UUID, terminal, etc.) y hace `POST {BOLD_API_URL}/payments/app-checkout` con la `x-api-key`.
- Config por `.env` (URL, key, terminal). Endpoint para iniciar el cobro.
- **Tests** (mock de la respuesta de Bold): body correcto, manejo de 201 y de errores AP00x.
- **Cierre:** suite verde.

## Wave 3 — Receptor del webhook 📩
- `POST /payments/bold/webhook`: recibe el resultado, **valida**, casa por `reference`, marca el `Payment` aprobado/rechazado **idempotentemente**.
- **Tests:** aprobado, rechazado, repetido (idempotencia).
- **Cierre:** suite verde + prueba end-to-end contra el mock (crear cobro → mock dispara webhook → pedido pagado).

## Wave 4 — Conectar el frontend 📱
- Traer el flujo de pago de la rama `wave-2-pago` y apuntarlo al backend nuevo.
- **Cierre:** UAT de Monica contra el mock.

## Fase 2 — Wompi (online) 🌐
- Adapter de Wompi (sandbox sin hardware) + su webhook. Milestone aparte cuando cerremos Bold.

## Despliegue
- El **mock NO va a producción** (es solo para desarrollo). El backend sí, con `.env` apuntando a sandbox/prod cuando haya credenciales reales.
