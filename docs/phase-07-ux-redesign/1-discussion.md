# Fase 7 — Rediseño UX · 1. Discussion

> Objetivo de Monica: que la app del cliente sea **moderna, llamativa y fácil de usar**, con todo bien organizado en categorías. (En progreso.)

## Contexto de marca (lo que ya sabemos)
- Marca: **Madre Mía — Arepas con Café de Origen** (La Macarena, Bogotá).
- Identidad activa en redes: `@madremiaarepasycafe`, emoji 🫓, estética artesanal (arepas ocañeras + café de origen).
- UI actual: mobile-first, cards por categoría, paleta terracota (`--accent: #d9622b`). Funcional pero básica.

## Lo que Monica quiere
- Visual **moderno y llamativo**.
- Todo en **categorías** claras.
- **Fácil de usar** para el cliente.

## Preguntas de la discusión (se irán respondiendo)
- [x] **Q1 — Referencias:** ✅ Referencia: **Crepes & Waffles** (elegante, cálido). Paleta deseada: **negro elegante + café/marrón + amarillo**. Vibra: elegante. (Pendiente: logo, screenshots de Instagram y foto del menú — Monica los enviará.)
- [ ] Q2 — Fotos: ¿tienen fotos de los platos? (las fotos cambian totalmente el diseño de un menú)
- [ ] Q3 — Vibra: ¿rústico/artesanal, minimalista moderno, colorido y divertido...?
- [ ] Q4 — Prioridad del cliente: ¿descubrir platos?, ¿pedir rápido?, ¿ver el café de origen como protagonista?
- [ ] Q5 — Idioma/público: ¿solo español? ¿turistas (La Macarena es zona turística)?

## Dirección visual (preliminar)
- **Referencia:** Crepes & Waffles → elegante, cálido, "premium accesible".
- **Paleta:** negro elegante + café/marrón + amarillo (acento). Encaja con "arepas con café de origen".
- **Assets a recibir:** logo, screenshots de Instagram, foto del menú físico → guardar en `docs/phase-07-ux-redesign/references/`.

## 🎯 Hallazgo clave: la marca ya define el diseño
Recibidos `logo.jpeg` y `menu.png` (la carta física). **La carta física es nuestra biblia de diseño:**
- **Paleta:** fondo **negro** (~`#0e0e0e`), acento **dorado/mostaza** (~`#c8a13a`), texto **blanco/crema**. (= el "negro + café + amarillo" que pidió Monica.)
- **Logo:** emblema circular (arepa con vapor + grano de café), monocromático.
- **Iconos de línea (line-art)** por categoría: arepa, taza de café, postre, vaso.
- **Tipografía** elegante, estilo hecho a mano; vibra artesanal-premium (tipo Crepes & Waffles).
- **Categorías** (coinciden con la BD): Arepas Ocañeras, Bebidas Calientes, Postres, Adiciones, Bebidas Frías.

➡️ **Dirección de diseño:** llevar la carta física a la app — rediseñar el menú del cliente con fondo negro, acentos dorados, el logo arriba, iconos por categoría y tipografía elegante.

## ⚠️ Tensión a resolver: fotos vs. tipográfico
- Monica quiere **fotos** de los platos (Q2 ✅ "con fotos sería genial").
- PERO la carta de marca es **tipográfica/elegante** (sin fotos, line-art).
- **Opciones:** (a) fiel a la marca = elegante tipográfico sin fotos; (b) full fotos estilo Rappi (se aleja de la marca y necesita 1 foto buena por plato); (c) **híbrido**: base negra/dorada elegante + foto donde haya (las del Instagram).
- **Pendiente:** ¿tienen foto buena de CADA plato, de algunos, o pocas? → decide el camino.

## Preguntas de la discusión (se irán respondiendo)
- [x] Q2 — Fotos: Monica las quiere. Falta saber de cuántos platos hay fotos (ver tensión arriba).

## Decisiones / hallazgos
- ✅ **Estilo:** llevar la carta física a la app — fondo **negro**, acentos **dorados/mostaza**, logo arriba, iconos de línea por categoría, tipografía elegante (vibra Crepes & Waffles).
- ✅ **Fotos: enfoque HÍBRIDO (C)** — base elegante negra/dorada + foto en los platos que sí tengan buena foto (tienen algunas). No se requiere fotografiar los 39.
- ✅ Categorías ya alineadas con la BD.

## 🔄 Revisión tras feedback de Rachel (2026-06-10)
Se probó en vivo el tema negro/dorado (Waves 1-2). Feedback de la dueña:
- ❌ Prefiere los **colores originales cálidos** (crema/terracota), no el negro/dorado.
- ❌ La barra de categorías mostraba el **scrollbar** y se veía mal.

**Decisiones revisadas:**
- ✅ **Paleta: 100% original (crema/terracota) + el logo** arriba (como badge). Se descarta el fondo negro.
- ✅ **Chips de categoría: se mantienen pero con el scrollbar OCULTO** (limpio, tipo Rappi).
- ↩️ El enfoque "llevar la carta negra a la app" se descarta; la marca aporta el **logo**, no el fondo negro.

## Siguiente etapa
→ **2. Research Plan:** patrones de UI para menús oscuros con fotos, accesibilidad/contraste, jerarquía visual, mejores prácticas de menú móvil. Luego **3. Execution** (rediseñar `index.css` + `App.tsx` con la nueva identidad).
