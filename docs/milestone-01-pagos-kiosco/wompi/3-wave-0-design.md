# Fase 2 · Wompi · Wave 0 — Diseño del flujo (decisiones)

> Diseño del pago **online** (cliente paga desde su celular: Nequi / PSE / tarjeta).
> Se llena con las decisiones de Monica. (Cerrado 2026-06-12.)

## Decisión 1 — ¿Dónde paga el cliente? ✅ (2026-06-12)
**Elegido: desde su PROPIO celular.** (No en una pantalla compartida.)

**Por qué:** más higiénico y privado — el cliente no teclea su tarjeta en una tablet
compartida. Es el modelo "paga desde tu teléfono".

**Hallazgo clave (de leer el código):** el cliente **ya está en su celular**.
El producto ya tiene **un QR por mesa** (`qr_codes/table_N.png`) que abre la ruta
`/table/N` (el menú del cliente, en `App.tsx`). O sea: escanea el QR de su mesa,
pide desde su teléfono y **paga en la misma página**. → **No hace falta un segundo QR
ni pasar sesión de una tablet al celular.** El Widget se abre ahí mismo.

## Decisión 2 — ¿Qué pantalla de pago de Wompi? ✅ (2026-06-12)
**Elegido: Widget (overlay).** La pantalla de Wompi aparece **encima** de nuestra app,
el cliente no "sale" a otra web. Unas líneas del JS de Wompi. (Descartado el redirect
Web Checkout: salir del navegador y volver es más frágil.)

**Importante:** como el cliente ya está en su celular, el Widget corre **en el celular
del cliente**, no en una tablet. No hay polling de una pantalla aparte.

## Flujo de pantallas
```
Cliente escanea el QR de su mesa  →  /table/3   (ya en SU celular)
        ↓  arma el pedido
[¿Cómo pagar?]   → toca "Pagar con Wompi"  (Nequi / PSE / Tarjeta)
        ↓
Backend prepara el cobro:  referencia única (UUID) + monto en CENTAVOS + FIRMA integridad
        ↓
Widget de Wompi se abre (overlay, mismo celular)  → el cliente paga
        ↓
┌─ El Widget devuelve el resultado a la página (transaction id)
└─ Wompi avisa al backend por webhook  (respaldo, idempotente, valida firma de eventos)
        ↓
Backend confirma con GET /transactions/<id>  ← fuente de verdad
        ↓
Marca el Payment aprobado  →  el pedido sale "💵 pagado" en cocina
        ↓
Pantalla "¡Pago exitoso!"  +  número de pedido
```

## Qué se reusa y qué es nuevo
**Reúso (de Bold):**
- Modelo `Payment` con `provider="wompi"`, `reference` UUID, status `pending → approved/declined`.
- Webhook idempotente (mismo patrón que el de Bold).
- El pedido **no** se marca "pagado" por el webhook; "pagado" se **deriva** del Payment
  (`Order.is_paid`) — igual que se decidió en el kiosco (Wave 0 de Bold, Decisión 5).

**Nuevo (lo propio de Wompi):**
- **Firma de integridad** (backend): `SHA-256("<referencia><monto_centavos><moneda><WOMPI_INTEGRITY_SECRET>")`.
  Es la pieza más delicada → se construye y se testea **sola** primero.
- **`wompi_gateway.py`**: prepara el cobro (firma) y consulta `GET /transactions/<id>`.
- **Endpoint** para iniciar el cobro (devuelve al front lo que el Widget necesita:
  llave pública, referencia, monto, firma).
- **Webhook** `POST /payments/wompi/webhook`: valida la **firma de eventos**
  (`WOMPI_EVENTS_SECRET`, distinta de la de integridad) y confirma con GET.
- **Front:** botón "Pagar con Wompi" en la pantalla de pago + cargar el Widget JS.

## Dos secretos distintos (no confundir) ⚠️
- `WOMPI_INTEGRITY_SECRET` (`test_integrity_…`) → firma el **cobro** al crearlo.
- `WOMPI_EVENTS_SECRET` (`test_events_…`) → valida la firma del **webhook** entrante.

## Dependencias / riesgos
- **URL pública para el webhook:** Wompi necesita poder hacer `POST` a nuestro backend.
  En local no llega → probar contra la **URL de Railway** (ya desplegado). Ver
  [[railway-deploy-notes]].
- **Montos en centavos:** COP × 100. Un error aquí = cobro 100× mayor/menor.
- **Referencia única por compra:** no se puede repetir (si no, Wompi la rechaza).

## Fuera de alcance ahora (futuro)
- **Tablet-kiosco compartida:** si algún local usa una sola pantalla compartida,
  ahí SÍ tocaría mostrar un QR para saltar al celular + que la tablet espere el
  resultado (polling). Hoy Rachel usa QR por mesa → no se construye.

## ✅ Wave 0 — Diseño CERRADO (2026-06-12)
Decisiones tomadas (dónde paga = celular vía QR de mesa; integración = Widget).
Llaves de sandbox ya recibidas. Siguiente: **Wave 1** — empezar por la **firma de
integridad** (pieza chica, testeable sola), luego el gateway, endpoint y webhook.
