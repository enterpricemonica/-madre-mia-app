# 🗺️ Roadmap — Madre Mía

> Visión: producto **reusable** de pedidos para restaurantes pequeños en Colombia (un "baby Toast"), empezando por **Madre Mía (Rachel)** como cliente cero. Conversación en español, código en inglés.

## Milestones

| # | Milestone | Estado | Resumen |
|---|-----------|--------|---------|
| **M1** | Pagos integrados (Bold) | ⏸️ Pausado | Rachel va **manual** (marca cómo pagó). El pago integrado (Bold/QR/webhook) quedó en la rama `wave-2-pago` para negocios que lo quieran. |
| **M2** | Reportes / cuadre de caja | ✅ **Hecho (prod)** | Pago manual (5 métodos) + reporte por día y método + descarga CSV (en hora Colombia). |
| **M3** | Facturación DIAN / impuestos | ⬜ Pendiente | IVA, impoconsumo, factura electrónica. Investigar proveedor. |
| **M4** | Multi-restaurante | ⬜ Pendiente | Que varios negocios lo usen: cada uno con su menú, tema **y página/storefront personalizable** (header + imágenes desde el admin). |
| **M5** | Offline / PWA | ⬜ Pendiente | App instalable, resiliencia a mala conexión, **notificaciones push**. |
| **M6** | UI moderna | 🚧 **En progreso** | Toasts, animación de carrito, skeletons, transiciones. Mantener la marca cálida, modernizar la ejecución. |
| **M7** | Lealtad / puntos | 💡 Idea futura | Programa de puntos/recompensas. Valioso, pero es su propio proyecto. |

## Notas de decisión
- **Página web personalizable por negocio** (header + imágenes desde admin) → pertenece a **M4** (es branding por-tenant). No urge para Rachel (dine-in: el cliente escanea el QR y va directo al menú).
- **Pagos:** Rachel no quiere dar credenciales de Bold → modo manual. El pago integrado es **opcional** para otros negocios (rama `wave-2-pago`).
- Prioridad actual: **M6**, arrancando por **toasts → animación de carrito → skeletons**.
