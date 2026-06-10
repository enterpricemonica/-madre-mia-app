# Fase 6 — Pagos · 2. Research Plan

> Investigación del panorama de pagos en Colombia (junio 2026). Con fuentes.

## Hallazgo principal: BOLD SÍ tiene API 🎯
BOLD (que el restaurante ya usa para el datáfono) **tiene un portal de desarrolladores y API de pagos en línea**:
- **API Link de Pagos:** se crea un link de pago con un `POST` al endpoint `/online/link/v1`. Ideal para cobrar sin construir checkout propio.
- **API de Pagos en Línea:** integración completa del cobro dentro de la propia app.
- **Métodos que acepta:** tarjetas crédito/débito, **PSE**, **Nequi**.
- **Requisito:** cualquier comercio registrado en BOLD con el producto de pagos activo puede aplicar a la integración.

➡️ **Implicación:** como la dueña ya tiene BOLD, integrar la API de BOLD es el camino más natural (un solo proveedor, el dinero llega donde ya está acostumbrada).

## Opciones de pasarela (comparativa)
| Pasarela | Comisión aprox. | Métodos clave | Notas |
|----------|-----------------|---------------|-------|
| **BOLD** | baja (de las más económicas) | Tarjetas, PSE, Nequi | Ya lo usa; API de links y checkout |
| **Wompi** (Bancolombia) | ~2.85% | Tarjetas, PSE, **Nequi**, **Daviplata**, botón Bancolombia, efectivo, BNPL | Integración por Widget o API; Nequi nativo |
| **ePayco** | ~2.68% + ~$900 | Tarjetas, PSE, efectivo (Efecty/Baloto) | Económica para pymes |
| **PayU** | ~3.49% | La mayor cobertura | Robusta, para negocios medianos/grandes |

> Nota: las comisiones cambian; verificar la tarifa vigente al momento de decidir.

## Bre-B (el rail nacional nuevo)
- **Qué es:** Sistema de Pagos Inmediatos e Interoperable del Banco de la República. En operación desde julio 2025, activación total octubre 2025. Ya mueve >5 millones de operaciones diarias.
- **Llaves:** identificadores (NIT, celular, email, alfanumérico, o **código de establecimiento** para comercios) que reciben dinero al instante. La "llave" que usa la dueña es esto.
- **QR:** Bre-B tiene **códigos QR** — se escanea y se inicia la transferencia al instante.
- **Implicación:** podríamos **mostrar el QR/llave Bre-B** en la app para que el cliente pague al instante desde su banco, sin pasarela ni comisión (es transferencia directa). Integración programática (API) aún es más nueva que BOLD/Wompi.

## Direcciones recomendadas (a debatir en Discussion)
1. **Mínimo viable (sin comisión):** la app muestra el total + **QR/llave de Nequi y Bre-B** para que el cliente pague al instante; el datáfono BOLD sigue para tarjetas presenciales. Cero integración, cero comisión.
2. **Pago en línea real:** integrar la **API de BOLD** (ya es su proveedor) o **Wompi** para cobrar tarjeta/PSE/Nequi dentro de la app. Útil sobre todo para **llevar/domicilio/prepago**. Costo: ~2.7–3.5% por transacción.
3. **Híbrido:** opción 1 por defecto + botón "pagar en línea" opcional con opción 2.

## Decisión que falta (de Discussion)
Depende de si el restaurante es solo para comer en el sitio (→ opción 1 suele bastar) o también para llevar/domicilio (→ opción 2 aporta mucho). Ver [1-discussion.md](1-discussion.md).

## Fuentes
- BOLD — API de pagos en línea / Link de pagos: https://developers.bold.co/pagos-en-linea/api-de-pagos-en-linea · https://developers.bold.co/pagos-en-linea/api-link-de-pagos · https://bold.co/pagos-en-linea/api/pagos-en-linea
- Wompi — métodos de pago: https://docs.wompi.co/en/docs/colombia/metodos-de-pago/ · https://wompi.com/es/co/que-es-wompi
- Bre-B (Banco de la República): https://www.banrep.gov.co/es/bre-b/que-es · Guía empresas 2026: https://www.mouvlatam.com/recursos/bre-b-empresas · Llaves: https://blog.bancolombia.com/educacion-financiera/llaves-sistema-de-pagos-inmediatos/
- Comparativa de pasarelas Colombia 2026: https://btodigital.com/pasarelas-pago-colombia-comparativa-guia-negocio/ · https://bytechhub.com/blog/pasarelas-de-pago-en-colombia-comparativa-2026/
