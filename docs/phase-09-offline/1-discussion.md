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

## Siguiente etapa
→ Research Plan: PWA con Vite (plugin `vite-plugin-pwa`), service workers, estrategias de caché, y cómo encolar peticiones offline.
