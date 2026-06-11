# Fase 9 — Resiliencia / Offline (PWA) · 1. Discussion

> Requisito de Monica: el internet en Colombia no siempre es bueno; la app debería funcionar incluso con mala conexión o cortes.

## La realidad técnica (importante)
La app es **cliente (celular) → backend en la nube (Railway) → cocina**. Si NO hay internet del todo:
- El cliente no puede ni cargar la app (vive en Vercel) salvo que ya esté cacheada.
- Un pedido nuevo **no puede llegar a la cocina** (debe viajar por internet).

➡️ Con esta arquitectura **cloud**, el flujo de pedido **no puede ser 100% offline**. Lo realista y muy valioso es hacerla **resistente a internet malo/intermitente** (el caso común).

## Qué SÍ se puede (resiliencia)
- **PWA** (Progressive Web App): la app se cachea y "se instala" en el celular → carga rápido y aguanta parpadeos de conexión.
- **Cachear menú y tema** → se ven aunque la conexión esté lenta/caída.
- **Detección de offline** → avisar al usuario ("sin conexión") en vez de fallar en silencio.
- **Cola de pedidos**: si el internet se cae justo al enviar, guardar el pedido localmente y reenviarlo al volver la conexión.
- **Reintentos** automáticos en las peticiones.

## Qué NO se puede (con esta arquitectura)
- Operar el restaurante **totalmente sin internet** de forma indefinida. Eso requeriría una arquitectura **local-first** (servidor local en el restaurante + sincronización) — mucho más compleja y probablemente excesiva para el tamaño del negocio.

## Preguntas para la discusión
- [ ] ¿El problema real es internet **lento/intermitente** (lo común) o **cortes largos** frecuentes?
- [ ] ¿Dónde duele más: que el **cliente** no pueda pedir, o que la **cocina/admin** se quede sin ver pedidos?
- [ ] ¿Vale la pena la cola de pedidos offline, o basta con que cargue rápido y reintente?

## 🔄 Decisión (tras confirmar con Rachel, 2026-06-10)
Rachel confirmó que el restaurante tiene **buen internet (5G, plan de 200 GB)**. Por lo tanto:
- ❌ **Se DESPRIORIZA el offline/local-first** — no aplica el problema de "internet malo" en el local. Sería sobre-ingeniería para el tamaño y la situación del negocio.
- 💡 Una **PWA ligera** (app instalable, carga rápida, ícono en el celular) queda como **mejora opcional futura** — barata y agradable, pero NO prioritaria.
- ✅ Seguimos con la arquitectura cloud actual, que es suficiente.

**Fase 9 → en pausa.** Retomar solo si más adelante aparece una necesidad real (ej. un local nuevo con mala conexión).

## Siguiente etapa (si se retoma)
→ Research Plan: PWA con Vite (plugin `vite-plugin-pwa`), service workers, caché del menú/tema.
