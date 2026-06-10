# Fase 7 — Rediseño UX · 2. Research Plan

> Mejores prácticas de UI para menú digital oscuro con fotos (junio 2026). Con fuentes.

## Decisiones de diseño (derivadas de la investigación + marca)
### Paleta (de la carta física)
- Fondo **negro suave** `#0f0f0f` (no negro puro — más elegante, menos fatiga visual).
- Tarjetas: dark cálido `#1a1814`.
- Texto cuerpo: crema/blanco `#f4efe6` (alto contraste, WCAG ≥4.5:1).
- Acento **dorado/mostaza** `#c8a13a` → títulos, precios, iconos. (No usar dorado para párrafos largos: bajo contraste.)
- Bordes sutiles `#2e2a22`.

### Layout
- **Mobile-first**, una sola columna.
- **Header** con el logo de Madre Mía arriba.
- **Barra de categorías fija (chips)** para saltar entre secciones (menú de 39 ítems es largo).
- Tarjeta por plato: nombre, descripción, precio en dorado, botón "+". **Foto donde haya** (bordes redondeados + sombra suave para integrarse al fondo oscuro).
- Mantener la **barra de carrito fija** abajo (ya existe), reestilizada.

### Buenas prácticas aplicadas
- Touch targets grandes y espaciados (fácil de tocar).
- Micro-copy opcional ("⭐ Favorito") en platos estrella (efecto serial position: destacar al inicio).
- Accesibilidad: `alt` descriptivo en fotos ("Foto de Arepa Vegetariana"), fuentes legibles.
- Imágenes livianas (carga rápida en datos móviles).

## Enfoque de fotos (híbrido — confirmado en Discussion)
- Base elegante negra/dorada SIN depender de fotos.
- Foto opcional por plato donde exista. Requiere un campo `image_url` en `MenuItem` (backend) que el admin pueda llenar. → Es una Wave aparte.

## Fuentes
- Dark mode UI 2026: https://www.tech-rz.com/blog/dark-mode-design-best-practices-in-2026/
- Menú digital que convierte: https://sundayapp.com/how-to-design-a-digital-menu-that-actually-converts/
- Menú accesible (restaurantes): https://blog.usablenet.com/quick-tips-to-help-your-restaurant-design-an-accessible-digital-menu-guest-blog
- Patrones de navegación móvil (NN/g): https://www.nngroup.com/articles/mobile-navigation-patterns/ · https://www.nngroup.com/articles/menu-design/
