# Hosting y costos

> Decisión sobre dónde corre Madre Mía y por qué. Investigado en junio 2026.

## La pregunta
¿Conviene tener la app en internet (cloud) o local en una computadora del restaurante? ¿Railway/Vercel se "apagan" solos?

## Respuesta corta
**Cloud (internet) es obligatorio** para esta app, porque es **de cara al cliente**: el cliente escanea un QR y usa **su propio celular** (muchas veces con datos móviles). Para que su celular llegue a la app, esta tiene que estar en internet. Un servidor **local** solo sería accesible en el WiFi del restaurante → los celulares en datos no podrían entrar. **Local NO es viable para el pedido por QR.**

## ¿Se apagan solos? (el mito del "1 minuto")
- **Vercel (frontend):** son archivos estáticos en una CDN → **siempre disponibles, sin apagarse, sin cold start**. Gratis. ✅
- **Railway (backend + DB):** **NO se apaga solo** a menos que actives el modo "serverless" (que duerme tras 10 min sin tráfico). En el plan de pago corre **24/7**. El "se apagan tras 1 minuto" aplica más al **free tier de Render** (duerme a los 15 min, con cold start de 30s-2min) — no es nuestro caso.

> Rachel **no tiene que prender/apagar nada**: una app en la nube está siempre encendida, automáticamente. Esa es justo la ventaja del cloud.

## El costo real
- **Vercel:** gratis (frontend estático).
- **Railway:** el trial da **$5 una vez** (30 días). Después, para que el backend + base de datos sigan 24/7, se necesita el plan **Hobby: ~$5/mes** (incluye $5 de uso). Una app pequeña como esta cabe de sobra.
- **Total realista: ~$5/mes (USD)** para tener todo siempre encendido. Para un negocio, es trivial.

## ¿Sirve un plan 100% gratis?
- **Frontend (Vercel free):** técnicamente funciona, PERO los términos del Hobby de Vercel son para **uso no comercial**. Para un negocio real, lo "correcto" sería Vercel Pro (~$20/mes) **o** mover el frontend a **Cloudflare Pages / Netlify**, que **sí permiten uso comercial en su plan gratis**. (Para empezar, Vercel free sirve; es una zona gris de términos.)
- **Backend + BD:** un plan gratis **NO alcanza** para una buena experiencia. Railway free da solo $1/mes (no mantiene 24/7). Render free **duerme** y el cliente esperaría 30s-2min al escanear → mala experiencia.
- **Conclusión:** lo barato y limpio es **~$5/mes (Railway Hobby)** para el backend+BD, y frontend gratis (Vercel, o Cloudflare Pages para estar 100% en regla). Para un negocio, $5/mes es mínimo.

## Decisión
- ✅ Quedarse en la **nube** (Vercel + Railway).
- ✅ Cuando se acabe el trial, pasar Railway a **Hobby (~$5/mes)**.
- ❌ Local descartado (no sirve para el QR de cara al cliente).

## Alternativas (si el costo importara)
- **Render:** free web service duerme a los 15 min (cold start lento → mala experiencia al escanear). Su DB free expira a los 90 días. No recomendado para algo de cara al cliente.
- **Fly.io:** tiene capa baja de costo, pero más complejo de operar.
- Conclusión: Railway Hobby (~$5/mes) es el mejor costo-beneficio por simplicidad.

## Fuentes
- Railway free trial / planes / app sleeping: https://docs.railway.com/pricing/free-trial · https://docs.railway.com/pricing/plans · https://docs.railway.com/reference/app-sleeping
- Vercel vs Render (cold starts / static always-on): https://render.com/docs/render-vs-vercel-comparison · https://northflank.com/blog/render-vs-vercel
