# M1 — Pagos integrados + Kiosco · 1. Discussion

> Etapa de discusión. Captura del brainstorm y las necesidades del negocio (junio 2026).
> Este milestone **reemplaza la conclusión de la Fase 6** (que era "solo mostrar el total + QR, sin pasarela"). Ver el porqué abajo.

## Qué cambió desde la Fase 6
El proyecto subió de nivel: además de servir a Rachel, ahora se construye como un **producto reusable** para restaurantes pequeños en Colombia (un "baby Toast"). Dentro de ese marco:
- **Solo en el sitio (dine-in) por ahora.** El pedido online/para llevar queda como futuro.
- Se decide construir el **pago integrado de verdad** (el cliente paga dentro de la app y la app se entera sola), no solo mostrar el total.

## El problema de Rachel (el dolor que resolvemos)
Rachel es **dueña única**. En días pesados **toma las órdenes Y cocina** a la vez: tiene que dejar la cocina, ir a la mesa, anotar en papel, y al final cobrar con el datáfono. Eso la frena y la estresa.

## La solución de este milestone
1. **Kiosco de autoservicio:** una pantalla fija en el local donde el cliente que llega pide **solo**, sin que Rachel pare de cocinar.
2. **Pago integrado en mesa Y kiosco:** el cliente paga **dentro de la app** (su celular en la mesa, o la pantalla del kiosco). Es el **mismo motor de pago** para las dos → se construye una vez.
3. **Confirmación automática:** cuando el pago se aprueba, la pasarela le avisa a nuestro backend (**webhook**) y el pedido **salta a cocina solo**. Rachel no marca nada a mano.

## Por qué cambiamos la decisión de la Fase 6
La Fase 6 concluyó "Opción 1: solo mostrar el total" porque para **dine-in con mesero** un cajero ya cobra. Pero el **kiosco no tiene cajero**: si el cliente tuviera que esperar a que Rachel deje la cocina para pasarle el datáfono, no ahorramos nada. **El kiosco solo funciona si el pago se cobra y se confirma solo.** Por eso pasamos a pago integrado (la "Opción B" que la Fase 6 dejó documentada como futuro).

## Preguntas resueltas en la discusión
- **¿El cliente elige cómo pagar?** Sí: el kiosco/mesa muestra "¿Cómo quieres pagar?" → Bre-B/QR, Nequi, tarjeta. El cliente selecciona.
- **¿Cómo sabe la app que el pago fue exitoso?** Por **webhook**: la pasarela (Bold) le pega a nuestro backend "pedido #N = APROBADO". No adivinamos ni confiamos en el cliente.
- **¿Necesitamos el QR de Bre-B de Rachel?** **No** el QR estático (una llave suelta no avisa a la app). El QR lo **genera la app** por cada pedido a través de Bold. Lo que se necesita son las **credenciales de Bold** (ver Dependencias).

## Decisiones confirmadas ✅
- ✅ Construir **kiosco de autoservicio** (pantalla fija en el local).
- ✅ **Pago integrado** en **mesa + kiosco**, mismo motor.
- ✅ Rail recomendado: **Bre-B / QR dinámico vía pasarela Bold** (Rachel ya tiene Bold), confirmado por **webhook**.
- ✅ Este milestone **reemplaza** la Opción 1 de la Fase 6.
- ✅ La **factura electrónica (DIAN)** NO entra aquí: es su propio milestone (M3).

## Dependencias (input de Rachel) 🔑
Para construir y probar de verdad necesitamos de la cuenta Bold de Rachel:
1. **Llaves de API (API keys)** — para que la app le hable a Bold.
2. Acceso para configurar el **webhook** en el panel de Bold.
3. Su **llave Bre-B registrada dentro de la cuenta Bold**, para que Bre-B aparezca como método.

> Mientras llegan, se puede avanzar todo en el **ambiente de pruebas (sandbox)** de Bold.

## Gaps / preguntas abiertas (a resolver durante el milestone)
- [ ] **¿Propina?** ¿La app sugiere propina antes de pagar, o no por ahora?
- [ ] **Cancelaciones/reembolsos:** ¿qué pasa si el cliente paga pero quiere anular? (probablemente lo maneja Rachel por fuera al inicio).
- [ ] **Pago a medias / abandono:** el flujo debe dejar el pedido SIN enviar a cocina si no se confirma el pago.
- [ ] **DIAN:** cobrar en la app probablemente obliga a factura electrónica → se aborda en **M3**, no aquí.

Ver el panorama técnico y de UX en [2-research-plan.md](2-research-plan.md), y el plan de construcción en [3-execution.md](3-execution.md).
