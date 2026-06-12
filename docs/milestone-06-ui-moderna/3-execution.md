# M6 — UI moderna · 3. Execution

> Waves. Rigor: esto es **cosmético** → verificación **visual** (UAT de Monica), no tests pesados.

## Wave 1 — Toasts 🔔
- Componente `Toast` + un contexto/hook (`useToast`) para lanzar mensajes desde cualquier pantalla.
- Reemplazar los `alert()` de `App.tsx`, `Admin.tsx`, `Kitchen.tsx` por toasts (éxito/error).
- Estilo: aparece, se desvanece solo, color según tipo.
- **Cierre:** UAT visual.

## Wave 2 — Animación del carrito 🛒
- "Pop" al tocar "+"; el contador/barra del carrito reacciona (rebote suave).
- CSS keyframes; respetar `prefers-reduced-motion`.
- **Cierre:** UAT visual.

## Wave 3 — Skeletons 💀
- Estado `loading` del menú → tarjetas fantasma con shimmer mientras llega la data.
- **Cierre:** UAT visual.

## Wave 4 (opcional) — Pulido 🎉
- Transiciones entre pantallas, estados vacíos con personalidad, check/confeti animado en "¡Pago exitoso!".

## Despliegue
- Frontend → Vercel. **Probar local primero**; subir cuando una wave esté **completa** (lección aprendida: no a medias).
