# 🗺️ Roadmap — Madre Mía

> Visión: producto **reusable** de pedidos para restaurantes pequeños en Colombia (un "baby Toast"), empezando por **Madre Mía (Rachel)** como cliente cero. Conversación en español, código en inglés.

## Milestones

| # | Milestone | Estado | Resumen |
|---|-----------|--------|---------|
| **M1** | Pagos integrados | ✅ **Hecho (prod)** | **Wompi online** (cliente paga desde el celular) + **propina voluntaria** (Ley 1935/2018, máx 10%), con UAT en vivo. Pago manual sigue disponible. Bold quedó opcional en la rama `wave-2-pago`. |
| **M2** | Reportes / cuadre de caja | ✅ **Hecho (prod)** | Pago manual (5 métodos) + reporte por día y método + CSV (hora Colombia) + **propina separada** (ventas netas / propinas / total). |
| **M3** | Facturación DIAN / impuestos | ⏸️ En pausa | Investigación hecha (`milestone-03-facturacion-dian/1-research.md`). **Depende de Rachel/su contador** (estado tributario, proveedor, presupuesto) → no se construye hasta tener esas respuestas. Monica decidió no meterse por ahora (2026-06-16). |
| **M4** | Multi-restaurante + vitrina | ⬜ Pendiente | Que varios negocios lo usen: cada uno con su menú, tema **y vitrina/storefront** (Inicio/Nosotros/Ordena aquí, editable desde admin). |
| **M5** | Offline / PWA | ⬜ Pendiente | App instalable, resiliencia a mala conexión, **notificaciones push**. |
| **M6** | UI moderna | ✅ **Hecho (prod)** | Toasts, animación de carrito, skeletons, y confeti + pop en "¡Pago confirmado!". Marca cálida, ejecución moderna. |
| **M7** | Lealtad / puntos | 💡 Idea futura | Programa de puntos/recompensas. Valioso, pero es su propio proyecto. |
| **M8** | Plantilla reusable / white-label | ✅ **Hecho (completo)** | Nombre, eslogan, saludo, logo y colores editables desde el admin (🎨); título de pestaña y **favicon** siguen al negocio (derivados del logo/nombre). Montar un restaurante nuevo = cambiar config, sin recodificar. **Enabler para vender a más restaurantes.** |
| **M9** | Menú multi-idioma | ⬜ Pendiente | El cliente ve el menú en varios idiomas (es/en). Útil en zonas turísticas. |
| **M10** | Control de inventario | ✅ **Hecho** | Stock opcional por plato (vacío = ilimitado), editable en el admin; se descuenta al vender (validado en servidor); el cliente ve "Agotado"/"Quedan X" y no puede pedir de más. |

## Notas de decisión
- **Vitrina/storefront personalizable** (Inicio/Nosotros/Ordena aquí, editable desde admin) → pertenece a **M4**. No urge para Rachel (dine-in: el cliente escanea el QR y va directo al menú). Idea revisada y aplazada conscientemente el 2026-06-15.
- **Pagos:** Wompi online en prod. Bold (datáfono) quedó **opcional** para otros negocios (rama `wave-2-pago`); Rachel no quiso dar credenciales de Bold.
- **Dirección de producto (2026-06-15):** Monica quiere **vender la app a más restaurantes**. Tras research de mercado, priorizó: **M8 (plantilla reusable)**, **M9 (multi-idioma)** y **M10 (inventario)**. M5 (offline) descartado para Rachel (buen internet). El "multi-tenant" pesado (muchos restaurantes en un deploy) NO es lo que quiere: prefiere 1 deploy por restaurante, fácil de re-vestir (white-label).
- **Próximo a decidir:** cuál de M8/M9/M10 construir primero.
