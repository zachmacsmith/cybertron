"""Selling to the window from a treasury (docs/review/31_institutions/03_money_labour.md §3.2 and #5; 08_integration.md item 0.11).

A convertible currency's window (set_convertible: the kernel's deposit and redeem actions) buys resources at the coin's price P and
mints coins for them. `deposit` is an agent's action on its own holdings, so a firm whose output sits in its treasury could only
turn it into money through an officer who withdrew it first. This module adds the law function

    sell_to_window(currency, item, qty)   the calling law's own treasury deposits qty of item into the currency's reserve and
                                          receives the coins at the current P (the same terms as an agent's deposit), into that
                                          treasury. Returns the coins received (0 when nothing was sold: a short treasury, a closed
                                          window, an item the currency does not convert to; the reason is recorded as a failed law
                                          call where law.call_failures is on).

law.v2 only (Kernel.api_for adds it under law.v2, with the dispatch helpers its callers use: treasury()). An association's law may
call it (lawapi CONTRACT_COLUMN "allow": it only ever spends its own treasury). Nothing calls it unless a law does, so no world
changes until one of its laws does. A polity whose treasury is the currency's own reserve (J0 without jurisdictions, whose treasury
is the reserve) has nothing to sell: the call returns 0.
"""
from __future__ import annotations

from cybertron import accounts as AC
from cybertron import credit as CR
from cybertron import jurisdictions as J
from cybertron import lawlang as L


def _fail(k, lid, reason, args) -> float:
    from cybertron import laweffects as LE
    k.w["effects"]["kernel_refusals"].append(reason)
    if LE.failures_on(k):                                               # law.call_failures: a failed call is told, as a move's is
        LE.call_failed(k, lid, "sell_to_window", list(args), reason)
    return 0.0


def sell(k, lid, currency, item, qty) -> float:
    """The law function: coins received by the law's treasury (0.0 when nothing was sold)."""
    cur = str(currency)
    item = str(item)
    c = k.w["currencies"].get(cur)
    if isinstance(qty, bool) or not isinstance(qty, (int, float)):
        raise L.LawError("sell_to_window: qty is a number")
    q = float(qty)
    args = (cur, item, q)
    if q <= 0:
        return 0.0
    if c is None:
        return _fail(k, lid, f"sell_to_window: no currency {cur}", args)
    if not c.get("convertible"):
        return _fail(k, lid, f"sell_to_window: {cur} is not convertible (no window)", args)
    if item not in k.w["unit"] or not k.unit_value(item):
        return _fail(k, lid, f"sell_to_window: {item} has no unit value and cannot be sold to the window", args)
    if c["convertible"] is not True and c["convertible"] != item:
        return _fail(k, lid, f"sell_to_window: {cur} converts only to {c['convertible']}", args)
    if not CR.redemption_open(k, cur):
        return _fail(k, lid, f"sell_to_window: {cur}'s window is closed (redemption suspended)", args)
    src = AC.treasury_of(k, AC.account_of(k, lid))
    rk = J.currency_reserve(k, cur)
    if src == rk:
        return _fail(k, lid, f"sell_to_window: this law's treasury is {cur}'s own reserve", args)
    if k.bal(src, item) + 1e-9 < q:
        return _fail(k, lid, f"sell_to_window: the treasury holds only {k.bal(src, item):g} {item}", args)
    if not c.get("par") and c["supply"] <= 1e-9:                        # first coins: as actions._deposit (the reserve's backing
        backing = sum(k.w["unit"].get(i, 0) * v for i, v in AC.holdings(k, rk).items())   # becomes treasury coins at P = 1)
        if backing > 1e-9:
            k.apply("mint", currency=cur, qty=backing, to=rk, via="treasury")
            k.log("treasury_coins", None, {"currency": cur, "coins": backing}, vis="public")
    coins = q * k.unit_value(item) / k.price(cur)
    if not k.move(src, rk, item, q, why=f"law:{lid}", by=None):
        return _fail(k, lid, f"sell_to_window: the move of {q:g} {item} to the reserve was refused", args)
    k.apply("mint", currency=cur, qty=coins, to=src, via="deposit")
    k.log("window_sale", None, {"law": lid, "treasury": src, "currency": cur, "item": item, "qty": q, "coins": coins,
                                "price": k.price(cur)}, vis="public")
    return coins


def law_api(k, lid) -> dict:
    """lawapi rows, module "window" (law.v2 only: Kernel.api_for adds it)."""
    def sell_to_window(currency, item, qty):
        return sell(k, lid, currency, item, qty)
    return {"sell_to_window": sell_to_window}
