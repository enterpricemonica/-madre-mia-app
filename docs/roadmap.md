# 🗺️ Roadmap — Madre Mía

> Visión: producto **reusable** de pedidos para restaurantes pequeños en Colombia (un "baby Toast"), empezando por **Madre Mía (Rachel)** como cliente cero. Conversación en español, código en inglés.

## Milestones

| # | Milestone | Estado | Resumen |
|---|-----------|--------|---------|
| **M1** | Pagos integrados | ✅ **Hecho (prod)** | **Wompi online** (cliente paga desde el celular) + **propina voluntaria** (Ley 1935/2018, máx 10%), con UAT en vivo. Pago manual sigue disponible. Bold quedó opcional en la rama `wave-2-pago`. |
| **M2** | Reportes / cuadre de caja | ✅ **Hecho (prod)** | Pago manual (5 métodos) + reporte por día y método + CSV (hora Colombia) + **propina separada** (ventas netas / propinas / total). |
| **M3** | Facturación DIAN / impuestos | ⬜ Pendiente | IVA, impoconsumo, factura electrónica. Investigar proveedor. (Legalmente importante para operar formal.) |
| **M4** | Multi-restaurante + vitrina | ⬜ Pendiente | Que varios negocios lo usen: cada uno con su menú, tema **y vitrina/storefront** (Inicio/Nosotros/Ordena aquí, editable desde admin). |
| **M5** | Offline / PWA | ⬜ Pendiente | App instalable, resiliencia a mala conexión, **notificaciones push**. |
| **M6** | UI moderna | ✅ **Hecho (prod)** | Toasts, animación de carrito, skeletons, y confeti + pop en "¡Pago confirmado!". Marca cálida, ejecución moderna. |
| **M7** | Lealtad / puntos | 💡 Idea futura | Programa de puntos/recompensas. Valioso, pero es su propio proyecto. |

## Notas de decisión
- **Vitrina/storefront personalizable** (Inicio/Nosotros/Ordena aquí, editable desde admin) → pertenece a **M4**. No urge para Rachel (dine-in: el cliente escanea el QR y va directo al menú). Idea revisada y aplazada conscientemente el 2026-06-15.
- **Pagos:** Wompi online en prod. Bold (datáfono) quedó **opcional** para otros negocios (rama `wave-2-pago`); Rachel no quiso dar credenciales de Bold.
- **Próximo a decidir:** M3 (facturación DIAN, legalmente importante) vs M5 (offline/PWA) vs M4 (multi-restaurante). Sin decisión tomada aún.
