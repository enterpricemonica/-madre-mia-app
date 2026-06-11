# M2 — Reportes de ventas · 1. Discussion

> Discusión y decisiones (junio 2026). Objetivo: que Rachel pueda **cuadrar la caja** al final del día.

## Para qué lo quiere Rachel
1. **Cuadrar la caja (principal):** cuánto entró hoy en total y **por cada método** (efectivo, datáfono, Nequi, Bre-B, tarjeta).
2. **Productos más vendidos** (secundario).
3. **Control de impuestos / contabilidad** (secundario).

## El hueco que descubrimos 🕳️
La app **solo sabe de los pagos que pasan por ella** (Bre-B/Nequi/tarjeta vía Bold). Pero Rachel también recibe **efectivo** y **datáfono**, que ocurren **por fuera** de la app. Si el reporte solo cuenta lo de la app, **no cuadra la caja completa.**

## Decisión: Opción A ✅
Para cuadrar **toda** la caja, **cada pedido termina con un registro de pago (`Payment`)**, sea como sea que pagó:
- Pagó por la app → ya tiene su `Payment` (lo crea el webhook).
- Pagó **efectivo** o **datáfono** → Rachel lo registra con un toque en la **pantalla de cocina** al cerrar el pedido → creamos un `Payment` "manual".

Así el reporte es **una sola cosa simple**: *"suma todos los pagos del día, agrupados por método"*. Reusa el modelo `Payment` que ya existe.

## Salida del reporte (confirmado) ✅
- 📍 Se ve en **`/admin`** (ya tiene login → solo Rachel ve las ventas).
- 📅 Por defecto **el día de hoy**; se puede **elegir otra fecha**.
- 📗 Descargable en **CSV** (se abre en Excel/Sheets). PDF queda para después si lo pide.

## Decisiones confirmadas ✅
- ✅ Objetivo principal: **cuadrar la caja** (total + desglose por método).
- ✅ **Opción A:** registrar método al cerrar el pedido (cocina) → todo pedido = un `Payment`.
- ✅ Reporte en `/admin`, por día (con selector de fecha), descarga **CSV**.
- ✅ Productos más vendidos e impuestos: se contemplan, pero el **cuadre** es lo primero.

Ver el plan técnico en [2-research-plan.md](2-research-plan.md) y [3-execution.md](3-execution.md).
