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

## Wave 3 — Fotos (híbrido) ✅ HECHA
- ✅ Backend: columna `image_url` (nullable) en `MenuItem` + en schemas (`MenuItemBase`).
- ✅ **Mini-migración** en `main.py` (`ensure_columns()`): `ALTER TABLE menu_items ADD COLUMN IF NOT EXISTS image_url` al arrancar → hace seguro el deploy sin Alembic ni pasos manuales en prod. (Alembic = mejora futura.)
- ✅ Admin: columna "Foto" con input por plato + campo en el formulario de "agregar".
- ✅ Cliente: miniatura en la tarjeta si el plato tiene `image_url` (`alt` descriptivo).
- ✅ **Hosting de fotos:** simple → archivos en `frontend/public/photos/`, servidos gratis por Vercel. El `image_url` es la ruta `/photos/nombre.jpg`. (No requiere bucket externo.)

## Wave 4 — Pulido
- Micro-copy ("⭐ Favorito"), animaciones suaves, estados vacíos bonitos.
- Revisar contraste/accesibilidad final.

## Deploy
- `git push` → Vercel (frontend) y Railway (si hubo cambios de backend en Wave 3).
