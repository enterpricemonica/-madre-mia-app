# M1 — Pagos integrados + Kiosco · 2. Research Plan

> Investigación de rails de pago, mecanismo de confirmación y UX del kiosco (junio 2026). Con fuentes.
> ⚠️ Las comisiones cambian: verificar las tarifas vigentes antes de implementar.

## A. Rails de pago en Colombia (comparativa)

| Opción | Qué es | Comisión aprox. | ¿Sirve para kiosco/mesa? |
|--------|--------|-----------------|--------------------------|
| **Bre-B (QR dinámico)** | Sistema de pagos inmediatos del Banco de la República (el "Pix" colombiano) | Casi 0% (transferencia) | ⭐ El mejor (escanear y listo) |
| **Bold (QR / API)** | Rachel **ya lo usa**; tiene API de desarrolladores | QR ~1.5% · link 3.29%+$900 · datáfono 2.89%+$300 | ✅ Reusa su cuenta |
| **Wompi** (Bancolombia) | Pasarela con buena documentación | Nequi 1.5% · tarjeta 1.99% · PSE 2.69% (+IVA) | ✅ Plan B |

**Conclusión:** en una pantalla de autoservicio, **teclear una tarjeta es mala UX**; **escanear un QR con el monto ya puesto** es lo más rápido y confiable. Bre-B es lo más barato y el cliente ya lo conoce (2.9M comercios a enero 2026). Como Rachel ya tiene **Bold**, lo usamos como pasarela: genera el QR dinámico **y** nos confirma por webhook.

## B. El corazón del milestone: confirmación por webhook

El problema central: **¿cómo sabe la app que el pago salió bien?**

- Una **llave Bre-B suelta** (transferencia directa a Rachel) **NO** avisa a la app. ❌
- Un cobro **a través de la pasarela (Bold)** genera un QR dinámico atado al pedido **y dispara un aviso automático (webhook)** a nuestro backend cuando se aprueba. ✅

**Bold soporta esto:**
- **Webhook:** se registra un endpoint HTTP POST en el panel de Bold (hasta 5). Bold le pega con el evento cuando cambia el estado de la transacción (incluye estado `APPROVED`/aprobado).
- **Consulta de estado (respaldo):** endpoint para consultar el estado de una transacción — sirve como *fallback* si el webhook se demora (la pantalla puede "preguntar" cada par de segundos).
- ⚠️ En **ambiente de pruebas NO llegan webhooks** → en sandbox probamos con la consulta de estado / simulación de venta.

**Flujo de pago (mesa o kiosco):**
```
1. Cliente arma pedido → "Pagar"
2. Pantalla: "¿Cómo quieres pagar?" → [Bre-B/QR] [Nequi] [Tarjeta]
3. Backend → Bold: "crea un cobro de $X para el pedido #N"  → Bold devuelve QR dinámico
4. Pantalla muestra QR + "Esperando tu pago…"
5. Cliente escanea con su app del banco/Nequi y paga
6. Bold → webhook → backend: "pedido #N = APROBADO"
7. Backend marca el pedido `paid` → salta a cocina SOLO
8. Pantalla: "¡Pago exitoso! Tu número es #N" → se reinicia
   (Si falla/timeout → NO entra a cocina, "intenta de nuevo")
```

## C. Seguridad (no negociable, es plata)
- **Validar la firma del webhook** (Bold/Wompi firman el evento) → nadie puede falsificar un "pagado".
- **El monto se calcula en el servidor** (ya lo hacemos) — el cliente nunca define cuánto paga.
- **Idempotencia:** un mismo webhook puede llegar dos veces; marcar `paid` una sola vez.
- El pedido **solo** pasa a cocina con confirmación real de la pasarela, nunca por acción del cliente.

## D. UX del kiosco — ⚠️ requiere decisiones de diseño front-end
El kiosco es una **pantalla nueva**, no es el menú del celular. **Esto implica decisiones de diseño** (Monica: esto es trabajo de front-end, lo decidimos juntas en la ejecución):
- **Modo kiosco:** una sola pantalla compartida por muchos clientes → debe **reiniciarse sola** entre cliente y cliente (timeout de inactividad → "¿Sigues ahí?" → vuelve al inicio).
- **Botones grandes**, pocos pasos, texto claro (lo usan personas sin la app, de una sola vez).
- **Pantalla de espera de pago** clara ("Esperando tu pago…") y de **éxito** (número de pedido grande).
- **Manejo de error/abandono** visible y sin dejar basura (pedido sin pagar no entra a cocina).
- **Hardware:** una tablet fija que Rachel prende en la mañana (modo pantalla completa / app "fijada").

## E. Reutilización (pensando en multi-restaurante, sin sobre-construir)
- Las **credenciales de Bold** deben venir de configuración (no hardcodeadas) → mañana cada restaurante pone las suyas. Por ahora basta con variables de entorno / settings; la tabla por-restaurante llega en **M4**.

## Fuentes
- Bold — webhooks: https://developers.bold.co/webhook · consulta de transacciones: https://www.developers.bold.co/pagos-en-linea/consulta-de-transacciones
- Bold — API Link de pagos / pagos en línea: https://developers.bold.co/pagos-en-linea/api-link-de-pagos · https://developers.bold.co/pagos-en-linea/api-de-pagos-en-linea · tarifas: https://bold.co/tarifas
- Wompi — eventos/webhooks: https://docs.wompi.co/en/docs/colombia/eventos-pagos-a-terceros/ · planes y tarifas: https://wompi.com/es/co/planes-tarifas/
- Bre-B (Banco de la República): https://www.banrep.gov.co/es/bre-b
