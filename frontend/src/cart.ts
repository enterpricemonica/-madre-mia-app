/**
 * Cart arithmetic, extracted from App.tsx so it can be tested without a browser.
 *
 * All of this decides money the customer sees, so it is worth testing on its
 * own rather than through a rendered screen. The authoritative total is still
 * computed by the backend from database prices — the client is never trusted —
 * but a wrong number here means the customer reads one price and is charged
 * another, which costs the restaurant trust even when the charge is correct.
 */

export type MenuItem = {
  id: number
  price: number
  /** null means unlimited; a number is the remaining stock (M10). */
  stock: number | null
}

/** itemId -> quantity */
export type Cart = Record<number, number>

/** What the cart adds up to, in whole Colombian pesos. */
export function cartTotal(menu: MenuItem[], cart: Cart): number {
  let total = 0
  for (const item of menu) {
    total += item.price * (cart[item.id] || 0)
  }
  return total
}

/** How many units are in the cart, across all dishes. */
export function cartItemCount(menu: MenuItem[], cart: Cart): number {
  let count = 0
  for (const item of menu) {
    count += cart[item.id] || 0
  }
  return count
}

export type AddResult =
  | { ok: true }
  | { ok: false; reason: 'sold-out' | 'not-enough'; remaining: number }

/**
 * May one more unit go into the cart?
 *
 * Only a guard for the customer's benefit; the server validates stock again on
 * checkout, because anything decided in the browser can be edited by the person
 * using it.
 */
export function canAddToCart(item: MenuItem | undefined, cart: Cart): AddResult {
  if (!item) return { ok: true }
  if (item.stock === null) return { ok: true }

  const inCart = cart[item.id] || 0
  if (inCart >= item.stock) {
    return item.stock <= 0
      ? { ok: false, reason: 'sold-out', remaining: 0 }
      : { ok: false, reason: 'not-enough', remaining: item.stock }
  }
  return { ok: true }
}

export type TipChoice = 'none' | 'p5' | 'p10' | 'other'

/**
 * The tip, in pesos.
 *
 * Colombian law (Ley 1935/2018) makes the tip voluntary and caps the suggested
 * amount at 10% of the bill, so every branch floors at the cap. `Math.floor`
 * throughout, because the backend validates against `order.total // 10` — integer
 * division — and a rounded-up peso would be rejected at checkout.
 */
export function tipAmount(orderTotal: number, choice: TipChoice, customTip = 0): number {
  const cap = maxTip(orderTotal)
  if (choice === 'p5') return Math.floor(orderTotal * 0.05)
  if (choice === 'p10') return cap
  if (choice === 'other') return Math.min(Math.max(customTip, 0), cap)
  return 0
}

/**
 * The most the customer may tip: 10% of the bill, floored.
 *
 * Exported so the screen can show the ceiling without restating the formula.
 * The cap lived in two places before — here and in the tip input's `max` — and
 * the day the law or the backend changes, two copies mean the app charges one
 * number while displaying another.
 */
export function maxTip(orderTotal: number): number {
  return Math.floor(orderTotal * 0.1)
}
