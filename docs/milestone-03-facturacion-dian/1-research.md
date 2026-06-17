# M3 — Facturación electrónica DIAN · Investigación

> Solo investigación (2026-06-16). NO se construyó nada. Objetivo: que Monica y Rachel
> decidan con información si/cómo seguir.

## TL;DR
- Un restaurante en Colombia **casi seguro está obligado** a facturar electrónicamente
  (es responsable del Impuesto Nacional al Consumo / impoconsumo).
- Desde el **1 julio 2024**, el recibo de papel POS **ya no es válido**: hay que emitir el
  **Documento Equivalente POS Electrónico (DEE POS)** y transmitirlo a la DIAN en tiempo real.
- Para integrarlo a la app se usa un **proveedor tecnológico** con API (Factus, Alegra, Siigo…).
- **Bloqueante:** antes de construir, Rachel debe confirmar su situación tributaria y si ya
  tiene contador/proveedor. Probablemente su contador ya maneja esto.

## 1. ¿Rachel está obligada?
- Los restaurantes/bares son responsables del **INC (impoconsumo, 8%)** → **obligados** a
  facturar electrónicamente.
- **Excepción:** persona natural con ingresos < **3.500 UVT** (~$183.309.000 en 2026) y que
  NO sea responsable de IVA → no obligada. Pero el INC suele activar la obligación igual.
- **Sanciones:** cierre del local hasta 3 días, o multa hasta ~$49.7M (950 UVT, UVT 2026 ≈ $52.374).
- ⚠️ **Decisión de Rachel/su contador:** confirmar su estado en el RUT (¿responsable de INC/IVA?).

## 2. Las DOS cosas que necesita un restaurante
1. **Documento Equivalente POS Electrónico (DEE POS)** — el "recibo" del día a día, para el
   cliente que NO pide factura (la mayoría). Se transmite a la DIAN en tiempo real, sin límite
   de monto. **Es el documento que la app emitiría en cada venta.**
2. **Factura Electrónica de Venta** — cuando un cliente (ej. una empresa) SÍ pide factura con
   su NIT para soportar el gasto. Menos frecuente, pero hay que poder emitirla.

## 3. Cómo funciona técnicamente
- Rachel debe **habilitarse como facturador electrónico** en la DIAN (sistema MUISCA) y tener
  una **resolución de numeración**.
- La app NO habla directo con la DIAN: habla con un **proveedor tecnológico** (autorizado por
  la DIAN) vía su **API**. El proveedor firma el documento, lo transmite a la DIAN y devuelve
  el documento válido (con **CUFE/CUDE** y **QR**) para mostrar/enviar al cliente.

## 4. Proveedores (con API) y costos aprox.
| Proveedor | Perfil | Costo aprox. | Notas |
|-----------|--------|--------------|-------|
| **Factus** | API liviana, SOLO facturación | ~$95.000 / 100 documentos | Docs para devs, sandbox, webhooks. La más "amigable para programar". |
| **Alegra** | Facturación + contabilidad | desde ~$17.900/mes; plan gratis bajo volumen | API abierta, habilitado DIAN, muy usado por pymes. |
| **Siigo** | Facturación + contabilidad | desde ~$9.992/mes facturación | Muy usado por contadores. |
| **DIAN gratis** | Portal oficial | $0 | **Manual** (sin API) → no se integra a la app; solo para cumplir a mano. |

> El costo del proveedor lo paga **el negocio** (Rachel), es recurrente. No es costo de desarrollo.

## 5. Esfuerzo de desarrollo (si construimos)
- **Medio-grande.** Integrar la API del proveedor, mapear datos (productos, **impoconsumo 8%**,
  NIT del cliente cuando pida factura), manejar la respuesta (guardar CUFE/QR), mostrar el
  documento. Manejar errores/reintentos (la DIAN a veces se cae).
- Necesita datos reales: **RUT de Rachel, resolución DIAN, credenciales del proveedor**.
- Ojo: implica manejar el **impoconsumo (8%)** en los totales → afecta precios/reportes.

## 6. Lo que depende de Rachel (no de nosotras) — antes de construir
- [ ] ¿Cuál es su situación tributaria? (¿responsable de INC/IVA? ¿obligada?)
- [ ] ¿Ya tiene **contador**? (casi seguro) ¿Qué proveedor usa él?
- [ ] ¿Ya está habilitada en la DIAN (MUISCA) con resolución de numeración?
- [ ] ¿Presupuesto mensual para el proveedor?
- [ ] ¿Quiere que la **app** emita el documento, o lo maneja aparte el contador por ahora?

## Recomendación
1. **No construir aún.** Primero Rachel responde el checklist de arriba (idealmente con su contador).
2. Si su contador ya usa Alegra/Siigo → integrar con **ese mismo** proveedor.
3. Si parte de cero y quiere algo "de programador" → **Factus** (API, sandbox, pago por documento).
4. Cuando haya respuestas, hacemos la fase de **research técnico** del proveedor elegido + plan en olas.

## Fuentes
- DIAN.com.co — obligados a facturar 2026
- Alegra — documento equivalente POS electrónico (preguntas frecuentes)
- Siigo — guía POS electrónico
- Factus — developers.factus.com.co
- niceeat.co — facturación electrónica para restaurantes
