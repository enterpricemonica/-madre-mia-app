import { describe, it, expect } from 'vitest'
import { cartTotal, cartItemCount, canAddToCart, tipAmount, maxTip } from './cart'

const arepa = { id: 1, price: 14000, stock: null }
const cafe = { id: 2, price: 5000, stock: 3 }
const agotado = { id: 3, price: 8000, stock: 0 }
const menu = [arepa, cafe, agotado]

describe('cartTotal', () => {
  it('adds up price by quantity', () => {
    expect(cartTotal(menu, { 1: 2, 2: 3 })).toBe(14000 * 2 + 5000 * 3)
  })

  it('is zero for an empty cart', () => {
    expect(cartTotal(menu, {})).toBe(0)
  })

  it('ignores a cart entry whose dish is no longer on the menu', () => {
    // A dish can be soft-deleted while sitting in someone's cart. It must not
    // be charged for, and it must not crash the total either.
    expect(cartTotal(menu, { 1: 1, 999: 5 })).toBe(14000)
  })
})

describe('cartItemCount', () => {
  it('counts units, not distinct dishes', () => {
    expect(cartItemCount(menu, { 1: 2, 2: 3 })).toBe(5)
  })
})

describe('canAddToCart', () => {
  it('allows a dish with unlimited stock', () => {
    expect(canAddToCart(arepa, { 1: 99 })).toEqual({ ok: true })
  })

  it('allows adding while stock remains', () => {
    expect(canAddToCart(cafe, { 2: 2 })).toEqual({ ok: true })
  })

  it('refuses once the cart already holds every remaining unit', () => {
    expect(canAddToCart(cafe, { 2: 3 })).toEqual({
      ok: false, reason: 'not-enough', remaining: 3,
    })
  })

  it('refuses a sold-out dish outright', () => {
    expect(canAddToCart(agotado, {})).toEqual({
      ok: false, reason: 'sold-out', remaining: 0,
    })
  })

  it('does not crash when the dish is unknown', () => {
    expect(canAddToCart(undefined, {})).toEqual({ ok: true })
  })
})

describe('tipAmount — the legal cap is the point', () => {
  it('is nothing when no tip was chosen', () => {
    expect(tipAmount(20000, 'none')).toBe(0)
  })

  it('gives 5% and 10% of the bill', () => {
    expect(tipAmount(20000, 'p5')).toBe(1000)
    expect(tipAmount(20000, 'p10')).toBe(2000)
  })

  it('never exceeds 10%, however generous the customer types', () => {
    // Ley 1935/2018 caps the suggested tip at 10%; the backend rejects more.
    expect(tipAmount(20000, 'other', 999999)).toBe(2000)
  })

  it('never goes negative', () => {
    expect(tipAmount(20000, 'other', -500)).toBe(0)
  })

  it('rounds DOWN, because the backend caps with integer division', () => {
    // 10% of 19999 is 1999.9. Rounding up to 2000 would exceed the backend's
    // 19999 // 10 = 1999 and the payment would be refused at checkout.
    expect(tipAmount(19999, 'p10')).toBe(1999)
    expect(tipAmount(19999, 'other', 99999)).toBe(1999)
  })

  it('handles an order of zero without dividing by anything', () => {
    expect(tipAmount(0, 'p10')).toBe(0)
  })
})

describe('maxTip — one definition of the legal ceiling', () => {
  it('is 10% of the bill, floored', () => {
    expect(maxTip(20000)).toBe(2000)
    expect(maxTip(19999)).toBe(1999)
    expect(maxTip(0)).toBe(0)
  })

  it('agrees with what tipAmount will actually charge', () => {
    // The screen shows maxTip as the ceiling; tipAmount enforces it. If these
    // two ever disagree, the customer is shown one limit and charged another.
    for (const total of [0, 999, 10000, 19999, 123456]) {
      expect(tipAmount(total, 'other', Number.MAX_SAFE_INTEGER)).toBe(maxTip(total))
      expect(tipAmount(total, 'p10')).toBe(maxTip(total))
    }
  })
})
