# M6 — UI moderna · 2. Research Plan

> Cómo lo construimos, técnicamente, **sin librerías pesadas** (liviano y fácil de mantener).

## Toasts
- Un componente propio sencillo + un **contexto** (o estado global ligero) para lanzar mensajes desde cualquier pantalla.
- Aparece (arriba o abajo), se **desvanece solo** (~3s), color según éxito/error.
- Reemplaza los `alert()` de `App.tsx`, `Admin.tsx`, `Kitchen.tsx`.
- Sin dependencia externa al inicio (un toast propio es chico y nos enseña el patrón de React Context).

## Animación del carrito
- **CSS** (transitions / keyframes): un "pop" (scale) en el botón al agregar; el contador/barra del carrito que rebota.
- Nada de JS pesado.

## Skeletons
- Mientras el menú carga, mostrar **tarjetas fantasma** grises con un brillo animado (shimmer) en CSS.
- Requiere un estado de "cargando" (hoy el menú llega y ya; agregamos `loading`).

## Principios
- **Solo CSS + React**, sin dependencias nuevas si se puede → rápido y mantenible.
- Respetar **`prefers-reduced-motion`** (accesibilidad): si el usuario pidió menos animación, la bajamos.
- Reusar las **variables de color del tema**.

## Fuentes
- Promodo / DesignStudio (tendencias UI 2026) · Restolabs (must-haves pedidos online) · Tubik (case study food app UI).
