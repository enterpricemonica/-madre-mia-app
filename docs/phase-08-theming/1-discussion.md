# Fase 8 — Configuración de tema (theming dinámico) · 1. Discussion

> Problema que resuelve: Monica no quiere editar código/CSS cada vez que cambian de opinión sobre los colores. Solución: una pantalla de configuración para cambiar el tema sin tocar código.

## Idea
- Una sección **"Configuración → Tema"** en el admin (protegida con login).
- Selectores de color (`<input type="color">`) para los colores clave.
- Los colores se **guardan en la base de datos** y la app los **aplica dinámicamente** sobreescribiendo las variables CSS (`:root`) al cargar.
- Resultado: cambiar colores = cero código.

## Arquitectura propuesta
- **Backend:** tabla `settings` (una fila) o key-value con los colores del tema. Endpoints: `GET /settings/theme` (público, lo necesita el cliente para pintar) y `PUT /settings/theme` (protegido).
- **Frontend:** al cargar, `fetch` del tema → `document.documentElement.style.setProperty('--accent', valor)` etc. Aplica a TODAS las pantallas (cliente, cocina, admin) porque comparten las variables.
- **Admin:** pantalla con color pickers + previsualización + guardar.

## Decisiones (Discussion) ✅
- [x] ¿Qué colores configurables? → **Set completo estilo Bootstrap (8):** Primary, Secondary, Success, Danger, Warning, Info, Light, Dark.
- [x] ¿Quién cambia el tema? → **Solo admin con login** (el cliente NO).

## Nota de alcance
La referencia de Monica fue el sistema de Bootstrap (Primary, Secondary, Success, Danger, Warning, Info, Light, Dark). Para un menú no necesitamos los 8 (Success/Warning/Info son estados de componentes). Proponemos un set enfocado a lo que de verdad querrán cambiar.
