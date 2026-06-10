# Fase 6 — Pagos · 3. Execution

> Plan técnico de la Opción 1 (mostrar total + QR de pago, cocina marca `paid`). Esfuerzo bajo.

## Dependencia (input de la dueña)
- 🔑 **Rachel debe dar su QR/llave de pago** (imagen del QR de Bre-B y/o Nequi). Es un QR fijo (no cambia por pedido); el cliente lo escanea y transfiere el total manualmente.

## Wave 1 — Mostrar total + QR de pago al cliente
**Frontend (`App.tsx`):** tras enviar el pedido, en vez de solo un `alert`, mostrar una pantalla/sección de confirmación con:
- El **total** a pagar.
- El **QR de pago** (imagen estática de Bre-B/Nequi en `assets/`).
- Texto: "Escanea para pagar $X por Bre-B o Nequi, o paga con datáfono/efectivo en caja".
- Número de pedido para referencia.

Sin cambios de backend (el pedido ya guarda el total).

## Wave 2 — La cocina marca `paid`
**Frontend (`Kitchen.tsx`):**
- Agregar la transición `delivered → paid` al mapa `NEXT_STATUS` con botón "💵 Marcar pagado".
- Mostrar también los pedidos `delivered` (hoy se filtran). Al marcar `paid`, desaparecen.

**Backend:** sin cambios — `PATCH /orders/{id}/status` ya acepta `paid` (está en `VALID_STATUSES`).

## Wave 3 (opcional) — Reporte simple de caja
- Una vista en `/admin` que liste los pedidos `paid` del día y su suma (control de ventas para Rachel).
- Backend: filtro por fecha/estado en `GET /orders`.

## Deploy
- `git push` → Railway + Vercel auto-deploy. Sin variables nuevas (salvo, si se quiere, una URL de imagen del QR).

## Fuera de alcance (futuro)
- Integración con API de BOLD/Wompi para cobro en línea (documentado en `2-research-plan.md`). Solo si abren prepago/domicilio propio.
- QR de Bre-B **dinámico** (con monto embebido) — requiere integración con el banco; el estático es suficiente por ahora.
