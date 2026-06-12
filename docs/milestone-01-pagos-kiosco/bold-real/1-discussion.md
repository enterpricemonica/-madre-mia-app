# M1 · Integración Bold REAL (vía mock) · 1. Discussion

> Retomamos el **pago integrado** (M1), ahora con la forma REAL de la API de Bold, pero contra un **mock local** — porque hoy no tenemos cuenta de Bold ni datáfono.

## El problema que resuelve
El pago integrado se había **pausado** porque (1) Rachel no quiere dar credenciales y (2) no teníamos cuenta Bold ni datáfono. Además, **el sandbox de Bold API Integrations exige un datáfono real vinculado.** → Por eso construimos un **MOCK** que simula a Bold (incluido el datáfono), y dejamos el código listo para cambiar a sandbox/producción **solo cambiando la URL base y la API key** (vía `.env`).

## Decisiones ✅ (Monica, 2026-06-11)
- ✅ Esto es el **M1 de Madre Mía** (la opción de pago integrado para negocios que la quieran), en este repo.
- ✅ El **mock server en Python (FastAPI)** — un solo lenguaje, igual que el backend.
- ✅ **Fase 1 = Bold (datáfono)**, **Fase 2 = Wompi** (online, su sandbox sí funciona sin hardware).
- ✅ Nunca hardcodear API keys (todo `.env`); referencias **UUID** por orden; **webhook idempotente**.

## Relación con lo existente
- En la rama `wave-2-pago` hay una versión **simplificada** del stub + el flujo de pago en el frontend. Esto lo **sube de nivel** a la API real de Bold (app-checkout con datáfono + webhook con `reference`). Evolucionamos eso.
- Reusa el modelo `Payment` que ya existe (la `reference` UUID y el `integration_id` viven ahí).

## Para quién aplica
Negocios que SÍ quieran cobro automático en el datáfono (Rachel sigue en manual). Es parte del producto reusable.
