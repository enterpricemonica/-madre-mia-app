# M1 · Integración Bold REAL · 2. Research Plan

> Spec técnica de **Bold API Integrations (datáfonos)**. Fuente oficial: developers.bold.co. Verificar contra la doc al pasar a sandbox/prod.

## Bold API Integrations (datáfono)
- **URL base real:** `https://integrations.api.bold.co`
- **Auth:** header `Authorization: x-api-key <llave_de_identidad>` en cada petición.
- **Endpoints:**
  - `GET /payments/payment-methods` → métodos: `POS`, `NEQUI`, `DAVIPLATA`, `PAY_BY_LINK`.
  - `GET /payments/binded-terminals` → datáfonos vinculados (`terminal_model`, `terminal_serial`).
  - `POST /payments/app-checkout` → inicia un cobro en el datáfono.
- **Body de app-checkout (obligatorios):** `amount {currency:"COP", taxes, tip_amount, total_amount}`, `payment_method`, `terminal_model`, `terminal_serial`, `reference` (UUID), `user_email`. Opcionales: `description`, `payer {email, phone_number, document}`.
- **Respuesta OK:** HTTP **201** con `integration_id`.
- **Resultado final:** llega por **WEBHOOK** (Bold notifica el estado usando la `reference` enviada). Webhooks separados para producción y sandbox.
- **Errores (400):** `AP002` taxes mal formado · `AP003` método inactivo · `AP004` datáfono no vinculado · `AP005` falta campo · `AP006` tipo incorrecto. `AP001` = 500.

## Montos mágicos del sandbox (los replica el mock)
| total_amount | Resultado |
|--------------|-----------|
| $1.000 – $2.000.000 | ✅ Aprobado |
| $111.111 | Fondos insuficientes |
| $222.222 | PIN inválido |
| $333.333 | Tarjeta expirada |
| $444.444 | Fallo de red |
| $999.999 | Rechazo general |

## Arquitectura
```
Frontend → Backend tienda (FastAPI) → [BOLD_API_URL] → Bold (mock | sandbox | prod)
                     ↑ webhook (resultado, con la reference)
```
- **Mock server (FastAPI, puerto aparte):** replica los 3 endpoints + la lógica de montos mágicos, y **dispara el webhook** a la tienda unos segundos después (simula el datáfono).
- **Backend tienda:** crea el cobro (arma el body + `reference` UUID) y recibe el webhook (idempotente).
- **Config `.env`:** `BOLD_API_URL`, `BOLD_API_KEY`, `BOLD_TERMINAL_MODEL`, `BOLD_TERMINAL_SERIAL` → cambiar entre mock/sandbox/prod sin tocar código.

## Reglas
- API keys solo en `.env` (nunca en el código).
- `reference` = UUID único por orden.
- Webhook **idempotente** (puede llegar repetido → marcar pagado una sola vez).

## Fase 2 — Wompi (online)
- Sandbox funciona **sin hardware**: registro en comercios.wompi.co, llaves `pub_test_`/`prv_test_`, API en `sandbox.wompi.co/v1`. Doc: docs.wompi.co.
