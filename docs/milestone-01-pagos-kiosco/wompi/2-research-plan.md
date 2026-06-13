# Fase 2 · Wompi · 2. Research Plan

> Cómo se integra Wompi (Colombia). Fuente: docs.wompi.co. Verificar contra la doc al implementar.

## Ambientes y llaves
- **Sandbox** (pruebas): `https://sandbox.wompi.co/v1`, llaves `pub_test_` / `prv_test_`.
- **Producción:** `https://production.wompi.co/v1`, llaves `pub_prod_` / `prv_prod_`.
- Sandbox y producción son **APIs separadas** (la info de uno no está en el otro).
- **Pública** → frontend (widget). **Privada** → backend (consultar transacción). **Secreto de integridad** → backend (firmar).

## Forma de integrar: Widget / Web Checkout
- **Widget:** unas pocas líneas de HTML/JS; el cliente paga **sin salir** de la app (overlay de Wompi).
- **Web Checkout (redirect):** un formulario que lleva al cliente a la pantalla segura de Wompi y luego lo devuelve a una URL nuestra con el `id` de la transacción.
- En ambos, **NO manejamos datos de tarjeta** → lo hace Wompi.

## Crear el cobro (parámetros clave)
- **Llave pública**, **moneda** (COP), **monto en CENTAVOS** (COP × 100), **referencia única** por compra (no se repite), y la **firma de integridad** (opcional pero recomendada).
- **Firma de integridad:** hash SHA-256 de `"<referencia><monto_en_centavos><moneda><secreto_integridad>"`. Se calcula en el **backend** (ahí vive el secreto).

## Recibir el resultado
- **Webhook (eventos):** Wompi hace un `POST` a la URL que configuremos, con el resultado de la transacción. Es la forma principal de enterarse.
- **Verificación:** también se puede consultar `GET {API}/transactions/<id>` (con la llave). Tras el redirect, el `id` viene en la URL.
- Validar la **firma del evento** del webhook (seguridad).

## Datos de prueba (sandbox)
- Se pueden simular transacciones **aprobadas / rechazadas / con error** (tarjetas y montos de prueba en la doc de "Datos de prueba en Sandbox").

## Arquitectura propuesta
```
Cliente toca "Pagar con Wompi"
   ↓
Backend prepara el cobro (referencia + monto en centavos + firma)   → wompi_gateway.py
   ↓
Cliente paga en el Widget/Checkout de Wompi (su pantalla)
   ↓
Wompi avisa por webhook  → POST /payments/wompi/webhook (idempotente, valida firma)
   ↓
Backend verifica con GET /transactions/<id> y marca el Payment aprobado
   ↓
El pedido queda "Pagado"
```
- Config por `.env`: `WOMPI_API_URL`, `WOMPI_PUBLIC_KEY`, `WOMPI_PRIVATE_KEY`, `WOMPI_INTEGRITY_SECRET`.
- Reusa el modelo `Payment` (provider="wompi", `reference` UUID, status pending→approved/declined).

## Fuentes
- Widget & Checkout Web: https://docs.wompi.co/docs/en/widget-checkout-web
- Ambientes y llaves: https://docs.wompi.co/docs/en/ambientes-y-llaves
- Datos de prueba en sandbox: https://docs.wompi.co/docs/en/datos-de-prueba-en-sandbox
