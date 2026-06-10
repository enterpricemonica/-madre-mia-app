# Fase 8 — Theming · 3. Execution (✅ HECHA)

## Backend
- Modelo `Theme` (tabla `theme`, fila única id=1) con los 8 colores Bootstrap. `create_all` crea la tabla (nueva, no necesita migración).
- Schemas `ThemeOut` / `ThemeUpdate`.
- `routers/settings.py`: `GET /settings/theme` (público — el cliente lo necesita para pintar) y `PUT /settings/theme` (protegido con `get_current_user`). `get_or_create_theme()` crea la fila con defaults la primera vez.

## Frontend
- `index.css`: definidos los 8 vars (`--primary`...`--dark`) y las variables de la app (`--bg`, `--accent`, `--text`, `--muted`) **derivadas** de ellos con `var()`. Cambiar un color Bootstrap repinta todo.
- `main.tsx`: al cargar, `fetch /settings/theme` y aplica cada color con `setProperty('--primary', ...)` → afecta cliente, cocina y admin.
- `Admin.tsx`: sección **🎨 Tema** con 8 color pickers (`input type=color`) + "Guardar tema" (PUT con token); al guardar, aplica los colores al instante.
- Conexiones semánticas: botón borrar = `--danger`; estados de cocina = `--primary`/`--warning`/`--success`.

## Resultado
Cambiar colores = **cero código**. El admin abre `/admin`, ajusta los colores y guarda. Resuelve el desgaste de editar CSS cada vez.

## Notas / futuro
- `--surface` (tarjetas, blanco) y `--border` no son configurables aún (se puede agregar).
- Migración: tabla nueva, sin pasos manuales. En prod se crea sola al desplegar.
