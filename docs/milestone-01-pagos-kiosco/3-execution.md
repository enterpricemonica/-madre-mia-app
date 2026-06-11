# M1 — Pagos integrados + Kiosco · 3. Execution

> Plan de construcción: features, waves, pruebas y despliegue.
> Regla de pruebas (definida con Dallas): **rigor basado en riesgo** — tests + datos mock + regresión **completos** en los flujos de plata/pedido; verificación manual más ligera en lo cosmético. Cada wave cierra con **UAT de Monica** antes de avanzar.

## Features (los bloques del milestone)
- **F1 · Motor de pagos (backend):** integración con la pasarela (Bold). Crear cobro, recibir/validar webhook, marcar el pedido `paid` de forma segura e idempotente. *Es el corazón; lo usan F2 y F3.*
- **F2 · Pago en la mesa (celular):** en el frontend actual del cliente, tras armar el pedido → elegir método → mostrar QR → esperar confirmación → éxito/fallo.
- **F3 · Kiosco (pantalla nueva):** modo autoservicio que reutiliza F1+F2, con reinicio automático entre clientes.
- **F4 · Configuración de credenciales:** las llaves de Bold por variables de entorno/settings (no hardcodeadas), listas para multi-restaurante (M4) sin construirlo aún.

## Modelo de datos (nuevo)
- **`Payment`** — `id`, `order_id`, `provider` (bold), `provider_ref` (id de transacción de Bold), `method` (bre_b / nequi / card), `amount`, `status` (pending/approved/declined), `created_at`, `updated_at`. Un pedido tiene un pago; el `status='approved'` es lo que marca el pedido `paid`.

## Waves (sprints entregables)

### Wave 0 — Preparación y diseño 🧩
- Conseguir credenciales **sandbox** de Bold y leer su API (link/cobro, webhook, consulta de estado).
- 🎨 **Decisiones de diseño del kiosco** (Monica + yo): pantallas, pasos, timeout, textos. *Entregable: bocetos/acuerdo de UI.*
- Definir el modelo `Payment` y los endpoints.
- **Cierre:** acuerdo de diseño + plan técnico aprobado. (Sin código de producción aún.)

### Wave 1 — Motor de pagos backend (sandbox) 💳
- Endpoint `POST /payments` → crea el cobro en Bold para un pedido y devuelve el QR/datos.
- Endpoint `POST /payments/webhook` → recibe el evento, **valida la firma**, marca `Payment.approved` + `Order.paid` (idempotente).
- Endpoint de respaldo: `GET /payments/{order_id}/status` (para que la pantalla consulte).
- **Pruebas (rigor alto):** tests con **datos mock** del webhook (aprobado, rechazado, duplicado, firma inválida); regresión del cálculo de total y del paso a cocina.
- **Cierre:** suite verde + UAT (simular venta en sandbox).

### Wave 2 — Pago en la mesa (celular) 📱
- En `App.tsx`: tras "Enviar pedido", pantalla de pago → selección de método → QR → "Esperando pago…" → éxito (número de pedido) / reintento.
- Conecta con F1; el pedido solo va a cocina cuando el backend confirma `paid`.
- **Pruebas:** flujo completo en sandbox (mock); regresión de que un pedido sin pagar NO llega a cocina.
- **Cierre:** UAT de Monica en celular real.

### Wave 3 — Kiosco 🖥️
- Pantalla nueva (ruta `/kiosco`) en **modo autoservicio**: botones grandes, menú → carrito → pago (reusa F1/F2) → éxito → **reinicio automático** (timeout de inactividad).
- Configuración de tablet (pantalla completa / app fijada).
- **Pruebas:** ciclo completo + reinicio entre clientes; que no quede estado de un cliente para el siguiente.
- **Cierre:** UAT de Monica en la tablet.

### Wave 4 — Endurecimiento y producción 🔒
- Pasar de **sandbox → producción** con las credenciales reales de Rachel (cuando las entregue).
- Manejo robusto de fallos/timeouts/reintentos; doble-llegada del webhook; revisión de seguridad.
- **Verificación end-to-end real** (un pago pequeño de verdad) en mesa y kiosco.
- **Cierre del milestone:** confirmar que se cumplen todos los requisitos → **archivar notas** y actualizar el [00-overview.md](../00-overview.md).

## Dependencias / bloqueos
- 🔑 **Credenciales de Bold de Rachel** (API keys + webhook + llave Bre-B en la cuenta). Hasta que lleguen, todo avanza en **sandbox**; solo la Wave 4 (producción real) queda bloqueada.

## Fuera de alcance (a propósito)
- **Factura electrónica DIAN** → **M3**.
- **Multi-restaurante** (credenciales por tenant en BD, onboarding) → **M4**; aquí solo dejamos las llaves configurables.
- **Propinas / reembolsos** → se decide en Wave 0 si entran como extra o se posponen.
- Pedido **online / para llevar** → futuro.

## Despliegue
- `git push` → Railway (backend) + Vercel (frontend) auto-deploy.
- Variables nuevas: credenciales de Bold (sandbox primero, producción después) y la URL pública del webhook.
