# Fase 2 · Wompi · 4. Ejecución (Wave 1)

> Lo que se construyó para el pago online con Wompi (cliente paga desde su celular).
> Estado: **código completo y probado (54 tests verdes); falta UAT en vivo**. (2026-06-12)

## Qué se construyó

### Backend
- **`backend/wompi_gateway.py`** — adapter de Wompi:
  - `integrity_signature(reference, amount_in_cents, currency, secret)` — firma SHA-256
    del cobro (`<ref><monto_centavos><moneda><secreto_integridad>`). Verificada contra el
    ejemplo oficial de Wompi.
  - `prepare_checkout(reference, amount_cop)` — arma+firma el paquete para el Widget.
    Convierte pesos→centavos (×100). **NO llama a Wompi por red** (a diferencia de Bold).
  - `get_transaction(transaction_id)` — `GET /transactions/<id>` con la llave privada.
    La **fuente de verdad** del estado del pago. Lanza `WompiError` si falla.
  - `verify_event_signature(event, secret)` — valida la firma de **eventos** del webhook
    (concatena valores de `signature.properties` + `timestamp` + secreto de eventos → SHA-256).
    Lee las `properties` del evento (no hardcodeadas). Compara con `hmac.compare_digest`.
- **`backend/routers/payments.py`**:
  - `POST /payments/wompi` — crea el `Payment` (pending, provider=wompi, reference UUID,
    monto del servidor) y devuelve el paquete firmado para el Widget.
  - `POST /payments/wompi/webhook` — valida firma de eventos → reconsulta con
    `get_transaction` → marca approved/declined (idempotente). Guarda el método real
    (Nequi/PSE/tarjeta) que solo se sabe al verificar.
- **`backend/schemas.py`** — `WompiCheckoutCreate`, `WompiCheckoutOut`.
- **`backend/.env` / `.env.example`** — 4 llaves: `WOMPI_API_URL`, `WOMPI_PUBLIC_KEY`,
  `WOMPI_PRIVATE_KEY`, `WOMPI_INTEGRITY_SECRET`, `WOMPI_EVENTS_SECRET`.

### Frontend (`frontend/src/App.tsx` + `App.css`)
- Carga el script del Widget (`https://checkout.wompi.co/widget.js`).
- Tras enviar el pedido → botón **"Pagar con Wompi"** → `payWithWompi()`:
  pide el cobro firmado, abre `WidgetCheckout` (mapea snake_case→camelCase,
  firma anidada `signature.integrity`).
- **Polling** `GET /payments/{order_id}/status` cada 3s (hasta ~1 min) → no le cree al
  callback del Widget, espera la confirmación del **webhook**.
- **Pantalla de confirmación**: spinner → ✓ "¡Pago confirmado!" / ✕ "No se completó".

## Tests
- `backend/tests/test_wompi.py` — **18 tests**: firma de integridad (incl. ejemplo
  oficial), prepare_checkout (pesos→centavos), get_transaction (Bearer + errores),
  endpoint (monto del servidor, ya-pagado, 404), firma de eventos (acepta válida,
  rechaza alterada/malformada), webhook (aprueba+marca pagado, **firma inválida→401**,
  idempotencia).
- Suite completa: **56 passed**. Frontend: `tsc --noEmit` y `npm run build` OK.

## Revisión pre-UAT (bugs encontrados y arreglados)
1. **`/payments/{order_id}/status` en reintentos:** hacía `.first()` sin ordenar → con un
   pedido que tuvo un intento rechazado + un reintento, devolvía el pago viejo (declined).
   Arreglo: priorizar `approved`; si no, el más reciente (`order_by(id.desc())`). +2 tests.
2. **Spinner infinito en el front:** si el webhook tardaba >1 min, el polling paraba pero
   la pantalla quedaba en `waiting` para siempre. Arreglo: estado `timeout` con salida clara
   ("Si ya pagaste, avísale al personal").

## Decisiones / hallazgos clave
- **Dos secretos distintos:** `WOMPI_INTEGRITY_SECRET` firma el cobro; `WOMPI_EVENTS_SECRET`
  valida el webhook. No confundir.
- **El front no confirma el pago:** la verdad la pone el webhook (firma + reconsulta).
  El polling es el puente para que la pantalla espere esa verdad del servidor.
- **Bug en la doc de Wompi:** el ejemplo de checksum del webhook está mal calculado
  (su hash no corresponde a su propia cadena). El algoritmo paso-a-paso sí es correcto.
  Ver memoria `wompi-doc-checksum-bug`.

## ✅ Checklist de despliegue
- [ ] Cargar las 4 llaves de Wompi en las **variables de entorno de Railway**
      (no van en git; hoy están solo en `backend/.env` local).
- [ ] Confirmar `WOMPI_API_URL=https://sandbox.wompi.co/v1` en Railway (sandbox para UAT).
- [ ] Desplegar backend y frontend.
- [ ] En el panel de Wompi (sandbox) → configurar la **URL de eventos (webhook)** apuntando
      a `https://<backend-railway>/payments/wompi/webhook`.
- [ ] Verificar que el frontend (`VITE_API_URL`) apunte al backend de Railway.

## ✅ Checklist de UAT (prueba en vivo, en celular)
- [ ] Escanear el QR de una mesa → abrir el menú en el celular.
- [ ] Armar un pedido → "Enviar pedido" → "Pagar con Wompi".
- [ ] El Widget de Wompi abre en el celular.
- [ ] Pagar con los **datos de prueba del sandbox** (tarjeta/monto aprobado).
- [ ] El webhook llega → el pago pasa a `approved` → la pantalla muestra "¡Pago confirmado!".
- [ ] En cocina (`/cocina`): el pedido aparece con el sello "💵 pagado".
- [ ] Probar también un pago **rechazado** (dato de prueba que declina) → pantalla de fallo.
- [ ] Revisar que el **método real** (Nequi/PSE/tarjeta) quedó guardado en el pago.

## Pendientes / futuro
- Validar la firma del webhook de **Bold** en sandbox/prod (TODO ya anotado en el código).
- "Tablet-kiosco compartida" (QR para saltar al celular) — fuera de alcance (ver wave-0-design).
- Posible: refrescar el estado del pedido en la pantalla del cliente sin recargar.
