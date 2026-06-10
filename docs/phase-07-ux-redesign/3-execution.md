# Fase 7 — Rediseño UX · 3. Execution

> Plan técnico del rediseño. Se construye en Waves.

## Wave 1 — Identidad visual (tema negro/dorado + logo) 🖤💛
- Reescribir la paleta en `index.css` (`:root`) → negro suave + dorado + crema.
- Copiar el logo a `frontend/public/logo.jpeg` y mostrarlo en el header del cliente.
- Reestilizar tarjetas del menú (`App.css`) para fondo oscuro.
- **Nota:** las variables son compartidas → cocina y admin también heredarán el tema oscuro. Revisar que se vean bien (ajustes menores si hace falta).

## Wave 2 — Navegación por categorías
- Barra de **chips de categorías** fija debajo del header; al tocar una, hace scroll a esa sección.
- Resaltar la categoría activa.

## Wave 3 — Fotos (híbrido)
- Backend: agregar columna `image_url` (nullable) a `MenuItem` + exponerla en schemas.
- Admin: campo para pegar/seleccionar la URL de la foto.
- Cliente: mostrar la foto en la tarjeta si existe (bordes redondeados, sombra, `alt` descriptivo).
- Hosting de imágenes: definir (URL pública; ej. subir a un bucket o usar las de Instagram/Drive).

## Wave 4 — Pulido
- Micro-copy ("⭐ Favorito"), animaciones suaves, estados vacíos bonitos.
- Revisar contraste/accesibilidad final.

## Deploy
- `git push` → Vercel (frontend) y Railway (si hubo cambios de backend en Wave 3).
