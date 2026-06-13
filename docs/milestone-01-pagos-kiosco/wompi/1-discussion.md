# Fase 2 · Wompi (pago online) · 1. Discussion

> Wompi es el pago **online** (el cliente paga desde su celular: tarjeta, PSE, Nequi). Distinto a Bold, que es el datáfono físico.

## ¿Por qué Wompi además de Bold?
- **Bold (datáfono):** staff pasa la tarjeta. Para negocios con datáfono.
- **Wompi (online):** el **cliente paga solo desde su celular**, sin hardware. Ideal para pedir y pagar en la mesa/kiosco o para llevar.

Su **sandbox funciona sin hardware**, así que sí podemos integrar contra el Wompi real en modo prueba.

## Decisiones ✅ (Monica, 2026-06-12)
- ✅ **Opción A:** integrar contra el **sandbox REAL de Wompi** (no mock). Monica se registra en `comercios.wompi.co` para obtener las llaves de prueba.
- ✅ Usar el **Widget / Web Checkout** de Wompi (su pantalla de pago lista) → **NO** tocamos datos de tarjeta (menos riesgo/legal).

## Dependencia (input de Monica) ✅ recibidas 2026-06-12
Del panel de Wompi (sandbox) son **4 llaves** (ojo: 2 secretos *distintos*):
1. **Llave pública** `pub_test_...` (frontend, para el widget).
2. **Llave privada** `prv_test_...` (backend, para consultar la transacción).
3. **Secreto de integridad** `test_integrity_...` (backend, firma el **cobro** al crearlo).
4. **Secreto de eventos** `test_events_...` (backend, valida la firma del **webhook**).

## Para quién aplica
Negocios que quieran que el cliente pague **online desde su celular**. Es otra forma de pago del producto (junto al manual y a Bold datáfono).
