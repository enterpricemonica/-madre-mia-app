# 🤖 Mock Bold API Integrations

Servidor que **se hace pasar por Bold** (API Integrations / datáfonos) para desarrollar
la integración de pagos SIN cuenta ni datáfono reales. **No va a producción.**

## Correr
```bash
# desde la raíz del proyecto, con el venv activo:
cd mock-bold
uvicorn main:app --port 9000
```

## Endpoints (iguales a los de Bold)
- `GET  /payments/payment-methods` → POS, NEQUI, DAVIPLATA, PAY_BY_LINK
- `GET  /payments/binded-terminals` → datáfonos "vinculados" (uno fake: MOCK-0001)
- `POST /payments/app-checkout` → inicia el cobro (201 + `integration_id`) y, unos
  segundos después, **dispara el webhook** a la tienda con el resultado.

Auth: header `Authorization: x-api-key <lo-que-sea>` (el mock solo verifica el formato).

## Montos mágicos (resultado del pago)
| total_amount | Resultado |
|--------------|-----------|
| 1.000 – 2.000.000 | ✅ Aprobado |
| 111.111 | Fondos insuficientes |
| 222.222 | PIN inválido |
| 333.333 | Tarjeta expirada |
| 444.444 | Fallo de red |
| 999.999 | Rechazo general |

## Config (variables de entorno, opcionales)
- `STORE_WEBHOOK_URL` (default `http://localhost:8000/payments/bold/webhook`)
- `MOCK_WEBHOOK_DELAY` segundos (default `3`)
