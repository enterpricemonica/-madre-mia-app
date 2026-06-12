# 📖 Guía simple — La integración de Bold (para estudiar con calma)

> Explicación en palabras sencillas de TODO lo que construimos para cobrar con el datáfono de Bold. Léela sin afán; al final sabrás exactamente qué hace cada pieza y dónde está.

---

## 🎯 ¿Qué queríamos lograr?
Que la app **cobre con el datáfono automáticamente**: el cliente pasa la tarjeta y la app **se entera sola** de si pagó, sin que nadie marque nada a mano.

## 🧠 Los 4 conceptos (con analogías)

1. **Bold** = la empresa del datáfono. Tiene una **API**: una "puerta" para que nuestra app le hable por internet (*"cóbrale $18.000 a este cliente"*).

2. **El mock** 🎭 = un **Bold falso**, como un maniquí o un doble de película. Lo hicimos porque **no tenemos cuenta de Bold ni datáfono reales**, y aún así queríamos construir y probar todo. El mock se ve y actúa como Bold, pero es de mentira.

3. **El webhook** 📞 = cuando **Bold nos llama a NOSOTROS** para avisar el resultado. Como pedir un domicilio: en vez de llamar cada rato preguntando *"¿ya?"*, **ellos te llaman** cuando está listo.

4. **El interruptor** 🔌 = un sí/no por negocio: *"¿este negocio cobra con Bold?"*. Apagado → el botón Datáfono marca manual (como Rachel hoy). Prendido → cobra con Bold de verdad. Así no rompemos a nadie.

## 🌊 El flujo completo (de punta a punta)
```
1. En la cocina, tocan "💳 Datáfono"
      → frontend/src/Kitchen.tsx  (función startBoldCharge)
2. El backend le pide el cobro a Bold
      → backend/routers/payments.py  (POST /payments/bold)
      → backend/bold_gateway.py      (arma el cobro y se lo manda a Bold)
3. "Bold" (el mock) recibe y simula el datáfono
      → mock-bold/main.py
4. El datáfono "termina" y Bold avisa por webhook
      → mock-bold/main.py            (dispara la llamada de vuelta)
      → backend/routers/payments.py  (POST /payments/bold/webhook)
5. El backend marca el pago aprobado → el pedido queda "Pagado"
      → la cocina lo refleja sola (pregunta cada 5 segundos = "polling")
```

## 📂 Dónde está cada pieza
| Pieza | Archivo | Qué hace |
|-------|---------|----------|
| El plan + la spec de Bold | `docs/milestone-01-pagos-kiosco/bold-real/` | Por qué y cómo; los datos técnicos de la API de Bold |
| El Bold falso (mock) | `mock-bold/main.py` | Se hace pasar por Bold; incluye los "montos mágicos" |
| El adapter | `backend/bold_gateway.py` | Le habla a Bold (POST app-checkout con la `x-api-key`) |
| Los endpoints | `backend/routers/payments.py` | `POST /payments/bold` (cobrar) y `POST /payments/bold/webhook` (recibir resultado) |
| El interruptor | `backend/models.py` (`Theme.bold_enabled`) y `frontend/src/Admin.tsx` (panel ⚙️) | Prender/apagar Bold por negocio |
| El botón inteligente | `frontend/src/Kitchen.tsx` | El botón Datáfono cobra con Bold o marca manual según el interruptor |
| La configuración | `backend/.env.example` (variables `BOLD_*`) | URL y llave de Bold → cambiar mock/sandbox/prod sin tocar código |
| Las pruebas | `backend/tests/test_bold.py` | Verifican el adapter y el webhook |

## ▶️ Cómo correrlo en tu compu
```bash
# 1) Backend de la tienda (necesita Postgres local corriendo)
cd backend && uvicorn main:app --port 8000

# 2) El Bold falso (en otra terminal)
cd mock-bold && uvicorn main:app --port 9000

# 3) Frontend (en otra terminal)
cd frontend && npm run dev
```
Luego: en `/admin` → ⚙️ → prende "Usar cobro con Bold". Haz un pedido en `/table/1`,
y en `/cocina` toca **💳 Datáfono** → verás "Cobrando…" → unos segundos → "Pagado".

## 🧪 Los "montos mágicos" del mock (para probar fallos)
| Monto | Resultado |
|-------|-----------|
| $1.000 – $2.000.000 | ✅ Aprobado |
| $111.111 | Fondos insuficientes |
| $222.222 | PIN inválido |
| $333.333 | Tarjeta expirada |
| $444.444 | Fallo de red |
| $999.999 | Rechazo general |

## 📝 Orden recomendado para estudiar
1. `docs/.../bold-real/2-research-plan.md` — qué es la API de Bold.
2. `mock-bold/main.py` — el Bold falso (lo más fácil de leer).
3. `backend/bold_gateway.py` — cómo le hablamos a Bold.
4. `backend/routers/payments.py` — los dos endpoints (cobrar + webhook).
5. `frontend/src/Kitchen.tsx` — el botón inteligente.

## 💥 Lección del deploy (importante)
Cuando el código usa una librería nueva (ej. `httpx`), **tiene que estar en `backend/requirements.txt`**, no solo instalada en tu compu. Si no, funciona local pero **el deploy se cae en producción** (le pasó a este proyecto el 2026-06-12). Regla: *si lo importas, va en requirements.txt.*
