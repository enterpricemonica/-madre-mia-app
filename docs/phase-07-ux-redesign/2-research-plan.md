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

## 🔬 Research Wave 4: primer contacto al escanear el QR + ¿fotos sí o no? (2026-06-10)
Qué espera el cliente HOY al escanear un QR (tendencias 2026):
- **Carga instantánea, sin descargar app** (✅ ya lo tenemos), móvil-primero.
- **Diseño visualmente atractivo**, NO un PDF con zoom. Layout limpio con **espacio en blanco**, jerarquía clara.
- **Destacar los platos estrella / favoritos** ("⭐ El más pedido") guía la decisión y se ve pro.
- Descripciones que antojen + info de alérgenos.
- Tipografía **sans-serif legible**, peso grueso, **alto contraste**.

**¿Fotos al lado de CADA producto? → NO.** Hallazgo clave:
- Las fotos suben ventas 20-45% (un plato con foto vende hasta 44% más) y reducen quejas de "no era lo que esperaba" (~40% menos).
- PERO **fotografiar TODO es un error**: un menú lleno de fotos se percibe como **comida rápida**, baja la sensación de calidad/premium. El punto óptimo es **fotografiar solo el 20-30% (los platos estrella)**.
- ➡️ **Esto valida nuestro enfoque HÍBRIDO**: foto solo en los destacados, el resto elegante y tipográfico. ¡Justo lo que construimos! (image_url opcional.)

**Decisiones de diseño Wave 4:**
- Header/hero más presente (logo mostaza + bienvenida + mesa) = mejor primer contacto.
- Fotos solo en ~20-30% (estrellas); badge "⭐ Favorito" en algunos.
- Tarjetas más pulidas (espaciado, hover, foto un poco más grande), más espacio en blanco, precio destacado.

## Fuentes
- Tendencias QR menú 2026: https://qrmenugenerator.io/blog/top-restaurant-technology-trends-for-2026-and-why-digitization-is-no-longer-optional · https://www.finedinemenu.com/en/blog/the-complete-qr-menu-guide-for-restaurants-everything-you-need-to-know-in-2026/
- Impacto de fotos (y por qué NO fotografiar todo): https://blog.csconnect.com/posts/how-restaurant-menu-photography-directly-correlates-to-higher-sales · https://foodshot.ai/blog/restaurant-food-photography-guide
- UX de menú digital: https://sundayapp.com/digital-menus-for-restaurants-a-step-by-step-guide/ · https://www.restolabs.com/blog/top-uiux-must-haves-online-ordering-websites-restaurants
- Dark mode UI 2026: https://www.tech-rz.com/blog/dark-mode-design-best-practices-in-2026/
- Menú digital que convierte: https://sundayapp.com/how-to-design-a-digital-menu-that-actually-converts/
- Menú accesible (restaurantes): https://blog.usablenet.com/quick-tips-to-help-your-restaurant-design-an-accessible-digital-menu-guest-blog
- Patrones de navegación móvil (NN/g): https://www.nngroup.com/articles/mobile-navigation-patterns/ · https://www.nngroup.com/articles/menu-design/
