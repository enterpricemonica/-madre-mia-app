# M1 · Wave 0 — Diseño del kiosco (decisiones)

> Acuerdo de diseño front-end del kiosco. Se va llenando a medida que Monica decide cada punto. (En progreso.)

## Decisión 1 — Layout del menú ✅ (2026-06-10)
**Elegido: cuadrícula con fotos + categorías al lado** (estándar de la industria: Toast, McDonald's, Panera).

**Por qué:** es el layout más usado y más efectivo — menos pasos = más ventas; las fotos suben el ticket promedio (la industria reporta +15% a +45%). Aprovecha el soporte de fotos que ya se agregó en la Fase 7.

**Detalle acordado:** cuadrícula rápida + un **mini-paso de adiciones** solo cuando el plato lo permita ("¿quieres agregarle algo?").

**Reglas de UI (de la investigación):**
- Categorías a la izquierda (5-7 máx), productos con foto a la derecha.
- Botones grandes, `+`/`–` claros, resumen del carrito siempre visible.
- Ítems agotados (`available=false`) salen en gris o no aparecen.
- Nombres de categoría que el cliente entienda (no jerga interna).

## Flujo de pantallas del kiosco (propuesto)
```
[Inicio / atraer]  "Toca para pedir"
        ↓
[Menú]  cuadrícula con fotos + categorías
        ↓  (mini-paso de adiciones si aplica)
[Carrito]  revisar, +/–, total
        ↓
[¿Propina?]  ← solo si está activada (ver Decisión 2)
        ↓
[¿Cómo pagar?]  Bre-B/QR · Nequi · Tarjeta
        ↓
[Esperando pago…]  muestra el QR dinámico
        ↓
[¡Pago exitoso!]  número de pedido grande
        ↓
[Reinicio automático]  vuelve a Inicio (timeout de inactividad)
```

## Decisión 2 — Propina ✅ (2026-06-10)
**Elegido: propina opcional y configurable, APAGADA por defecto.**

**Cumple la Ley 1935 de 2018:** voluntaria, sugerida **máx. 10%** (sin impuestos), nunca automática, informada como voluntaria. La propina **no es ingreso del restaurante** → pertenece a los trabajadores (se registra aparte).

**Cómo se construye:**
- Un setting en el admin para **prender/apagar** la propina (queda listo para multi-restaurante: cada local decide).
- Si está prendida: pantalla "¿Quieres dejar propina?" con `0% / 10% / otro`, clarito que es voluntaria.
- Para Rachel: **apagada**, y se lo confirmamos a ella (es su plata y su decisión).

## Decisión 3 — Inicio y reinicio automático ✅ (2026-06-10)
- **Pantalla de inicio:** logo + nombre + foto apetitosa + botón grande **"Toca para pedir"**.
- **Reinicio:** tras **45s sin tocar** → aviso **"¿Sigues ahí?"** con cuenta regresiva de **10s** → si no responde, **borra el pedido y vuelve al inicio**; si toca "Sí, sigo", continúa. Tiempos ajustables.

## Decisión 4 — Adiciones ✅ (2026-06-10)
**Elegido: "empujoncito" después de agregar** (adiciones como líneas aparte, reusando el modelo actual).

- Al agregar un plato que admite adiciones → mini-aviso "¿Quieres agregarle algo?" con botones de adición (+Queso, +Carne…).
- La adición entra como **línea propia** en el pedido (no atada técnicamente al plato). En cocina se ve el plato y debajo la adición.
- **No se cambia el modelo de datos** ahora (no sobre-construimos). Upgrade a "modificadores" reales = futuro (posible M4).

---

## ✅ Wave 0 — Diseño CERRADO (2026-06-10)
Las 4 decisiones de diseño del kiosco están tomadas (layout, propina, inicio/reinicio, adiciones). Falta para arrancar la **Wave 1 (motor de pagos)**:
- 🔑 **Dependencia:** crear cuenta/credenciales **sandbox de Bold** (bloquea el código de pagos).
- El modelo `Payment` y los endpoints ya están esbozados en [3-execution.md](3-execution.md).
