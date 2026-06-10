# Fase 6 — Pagos · 1. Discussion

> Etapa de discusión. Captura del brainstorm y las necesidades del negocio. (En progreso.)

## Contexto del negocio (investigado)
- **Madre Mía — Arepas con Café de Origen**, barrio La Macarena, Bogotá (Cl 26b #4-38).
- Horario: Lun-Mié 12:00-20:00, Jue-Sáb 12:00-21:00.
- Especialidad: arepas ocañeras + café de origen. Arepas $13.000-$25.000, bebidas $5.000-$8.000.
- **Servicio en el sitio (dine-in)** para nuestra app. Los **domicilios ya los maneja Rappi** (canal aparte) → nuestra app NO necesita resolver pago de domicilios.
- Marca activa en redes: Instagram/TikTok/Facebook `@madremiaarepasycafe` (útil para el rediseño UX, Fase 7).

## Cómo cobra HOY el restaurante
La dueña recibe pagos por **5 vías**:
1. **Nequi** (transferencia / QR)
2. **Daviplata** (transferencia / QR)
3. **Datáfono BOLD** (tarjetas, presencial)
4. **Llave Bre-B** (sistema de pagos inmediatos del país)
5. **Efectivo (cash)**

> Hoy el pago ocurre **al final, en la mesa**, por fuera de la app. La app solo registra el pedido.

## Lo que Monica quiere explorar
- ¿Se puede **integrar BOLD** en la app? ¿Hay otras opciones?
- ¿Cómo serían los **pagos en línea** dentro de la app?
- ¿Cómo nos comparamos con otras apps pagas del mercado? ¿Qué nos falta para ser competitivos?

## La pregunta pivote (a decidir)
**¿El cliente paga DENTRO de la app, o se sigue cobrando como hoy y la app solo registra el pedido?**
- **Opción A — Registrar (como hoy):** el cliente pide por la app; paga en la mesa con datáfono/Nequi/Bre-B. Cero integración, cero comisiones, cero riesgo. La app puede *mostrar* el total y un QR de pago.
- **Opción B — Pago en línea en la app:** el cliente paga al pedir (ideal para llevar/domicilio/prepago). Requiere integrar una pasarela (BOLD/Wompi). Tiene comisión (~2.7–3.5%).
- **Opción híbrida:** registrar por defecto + ofrecer "pagar ahora" opcional.

## Conclusión preliminar de la discusión
Como el servicio es **solo en el sitio** (los domicilios los cubre Rappi) y ya aceptan 5 medios de pago, **el pago en línea con pasarela aporta poco y suma comisión (~3%)**. La estrategia recomendada para la Fase 6 es la **Opción 1 (sin comisión):**
- La app **muestra el total** del pedido al cliente.
- Ofrece **pagar al instante** mostrando el **QR de Bre-B / Nequi** (transferencia directa, 0% comisión).
- El **datáfono BOLD y el efectivo** siguen igual para quien prefiera.

Esto es de **bajo esfuerzo técnico** y **cero comisión** → muy buen costo-beneficio. El pago en línea con API (BOLD/Wompi) queda documentado como opción futura si algún día abren su propio domicilio/prepago.

## Decisiones confirmadas ✅
- ✅ **Opción 1** (mostrar total + QR de Bre-B/Nequi, sin pasarela, sin comisión).
- ✅ La **cocina marca el pedido como `paid`** (transición `delivered → paid`).
- ✅ Equipo pequeño (Rachel sola o +1) → **sin roles complejos**; cocina = admin.

Ver opciones técnicas y comisiones en [2-research-plan.md](2-research-plan.md).
