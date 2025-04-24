


from datamodel import TradingState, OrderDepth, Order
from typing import List, Dict
import numpy as np
import json
import math

def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def black_scholes_call(r: float, S: float, K: float, T: float, sigma: float) -> float:
    if T <= 0 or sigma <= 0:
        return max(S - K, 0.0)
    d1 = (math.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*math.sqrt(T))
    d2 = d1 - sigma*math.sqrt(T)
    return S*norm_cdf(d1) - K*math.exp(-r*T)*norm_cdf(d2)

class Trader:
    def __init__(self):
        #Volcanic Rock vouchers
        self.base_threshold = 0.05
        self.exit_threshold = 0.02
        self.trade_size = 10
        self.pos_limit = 200
        self.r = 0.0
        self.sigma = 0.2
        self.TTE = 4
        self.vouchers = {
            "VOLCANIC_ROCK_VOUCHER_9500": 9500,
            "VOLCANIC_ROCK_VOUCHER_9750": 9750,
            "VOLCANIC_ROCK_VOUCHER_10000": 10000,
            "VOLCANIC_ROCK_VOUCHER_10250": 10250,
            "VOLCANIC_ROCK_VOUCHER_10500": 10500
        }
        # Counterparty threshold tweaks
        self.cp_adjust = {
            "Beetle": +0.02,
            "Cockroach": +0.02,
            "Ant": -0.01,
            "Spider": 0.0,
            "Mosquito": -0.02
        }

        # Magnificent Macarons
        self.weights = {
            "bidPrice": 0.48606,
            "askPrice": 0.51281,
            "transportFees": 0.02976754,
            "exportTariff": -0.0842141,
            "importTariff": -0.06292103,
            "sugarPrice": -0.00162174,
            "sunlight": -0.00577173
        }
        self.intercept = 1.955586762815983
        self.base_conv = 10
        self.macaron_pos_limit = 75

    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        conversions = 0

        # restore memory
        raw = state.traderData or ""
        try:
            mem = json.loads(raw)
        except:
            mem = {}
        cp_scores = mem.get("cp_scores", {})
        bought_last = mem.get("bought_last", False)

        # update counterparty PnL
        for prod, trades in state.own_trades.items():
            for t in trades:
                if t.buyer == "SUBMISSION" and t.seller:
                    cp_scores[t.seller] = cp_scores.get(t.seller, 0.0) - t.price * abs(t.quantity)
                if t.seller == "SUBMISSION" and t.buyer:
                    cp_scores[t.buyer] = cp_scores.get(t.buyer, 0.0) + t.price * abs(t.quantity)

        # identify last counterparty & adjust threshold 
        last_cp = None
        for prod, trades in state.own_trades.items():
            for t in trades:
                if getattr(t, "counter_party", None):
                    last_cp = t.counter_party
        cp_type = last_cp.split()[-1] if last_cp else None
        adjust = self.cp_adjust.get(cp_type, 0.0)
        threshold = self.base_threshold + adjust

        # Round 1 Algo
        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: list[Order] = []

            if product in ["RAINFOREST_RESIN"]:
                
                fair_price_RR = 9999.99655
                std_price_RR = 1.4965920476507821
                acceptable_price = fair_price_RR
                position_limit = 10
                current_pos = state.position.get(product, 0)
                
                
                mm_limit = 40
                if current_pos <= 0:
                    volume = mm_limit + current_pos
                else:
                    volume = mm_limit - current_pos
    
                my_ask_volume = -volume
                my_bid_volume = volume
    
                my_bid = int(round(fair_price_RR - 1.5 * std_price_RR, 2))
                my_ask = int(round(fair_price_RR + 1.5 * std_price_RR, 2))
    
                
                print(f"Market-Making RR BUY {my_bid_volume}x @ {my_bid}")
                orders.append(Order(product, my_bid, my_bid_volume))
                print(f"Market-Making RR SELL {-my_ask_volume}x @ {my_ask}")
                orders.append(Order(product, my_ask, my_ask_volume))
    
                if order_depth.sell_orders:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]
                    
                    if best_ask < acceptable_price:
                        buyable_volume = min(-best_ask_volume, position_limit - current_pos)
                        if buyable_volume > 0:
                            print(f"BUY RR {buyable_volume}x @ {best_ask}")
                            orders.append(Order(product, best_ask, buyable_volume))
    
                if order_depth.buy_orders:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    
    
                    if best_bid > acceptable_price:
                        sellable_volume = min(best_bid_volume, position_limit + current_pos)
                        if sellable_volume > 0:
                            print(f"SELL RR {sellable_volume}x @ {best_bid}")
                            orders.append(Order(product, best_bid, -sellable_volume))
    
                result[product] = orders

            if product in ["KELP"]:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                current_pos = state.position.get(product, 0)
                fair_price_kelp = (best_ask + best_bid) / 2
    
                mm_limit = 50
                if current_pos <= 0:
                    volume = mm_limit + current_pos
                else:
                    volume = mm_limit - current_pos
        
                my_ask_volume = -volume
                my_bid_volume = volume
        
                my_bid = int(round(fair_price_kelp - 1.5, 2))
                my_ask = int(round(fair_price_kelp + 1.5, 2))
    
                print(f"Market-Making BUY KELP {my_bid_volume}x @ {my_bid}")
                orders.append(Order(product, my_bid, my_bid_volume))
                print(f"Market-Making SELL KELP {-my_ask_volume}x @ {my_ask}")
                orders.append(Order(product, my_ask, my_ask_volume))
                    
                result[product] = orders

            if product in ["SQUID_INK"]:
                continue


        # Volcanic Rock Voucher Logic (Round 3 Algo)
        if "VOLCANIC_ROCK" in state.order_depths:
            vr = state.order_depths["VOLCANIC_ROCK"]
            if vr.buy_orders and vr.sell_orders:
                St = (max(vr.buy_orders) + min(vr.sell_orders)) / 2
                m_vals, v_vals, mid_info = [], [], {}
                for sym, K in self.vouchers.items():
                    od = state.order_depths.get(sym)
                    if not od or not od.buy_orders or not od.sell_orders:
                        continue
                    bid, ask = max(od.buy_orders), min(od.sell_orders)
                    mid = (bid + ask) / 2
                    m = math.log(K/St) / math.sqrt(self.TTE)
                    v = black_scholes_call(self.r, St, K, self.TTE, self.sigma)
                    m_vals.append(m)
                    v_vals.append(v)
                    mid_info[sym] = {"bid": bid, "ask": ask, "mid": mid}

                if len(m_vals) >= 2:
                    a, b, c = np.polyfit(m_vals, v_vals, 2)
                    for sym, K in self.vouchers.items():
                        info = mid_info.get(sym)
                        if not info:
                            continue
                        m = math.log(K/St) / math.sqrt(self.TTE)
                        fitted = a*m*m + b*m + c
                        dev = info["mid"] - fitted
                        pos = state.position.get(sym, 0)
                        od = state.order_depths[sym]
                        orders = []

                        if dev > threshold:
                            qty = min(self.trade_size,
                                      od.buy_orders[info["bid"]],
                                      pos + self.pos_limit)
                            if qty > 0:
                                orders.append(Order(sym, info["bid"], -qty))
                        elif dev < -threshold:
                            qty = min(self.trade_size,
                                      abs(od.sell_orders[info["ask"]]),
                                      self.pos_limit - pos)
                            if qty > 0:
                                orders.append(Order(sym, info["ask"], qty))
                        elif abs(dev) < self.exit_threshold:
                            if pos > 0:
                                q = min(pos, od.buy_orders[info["bid"]])
                                if q > 0:
                                    orders.append(Order(sym, info["bid"], -q))
                            elif pos < 0:
                                q = min(-pos, abs(od.sell_orders[info["ask"]]))
                                if q > 0:
                                    orders.append(Order(sym, info["ask"], q))

                        if orders:
                            result[sym] = orders

        # Magnificent Macarons Logic (REVERSED) (Round4 Algo)
        if "MAGNIFICENT_MACARONS" in state.order_depths:
            depth = state.order_depths["MAGNIFICENT_MACARONS"]
            pos = state.position.get("MAGNIFICENT_MACARONS", 0)

            if depth.buy_orders and depth.sell_orders:
                best_bid = max(depth.buy_orders)
                best_ask = min(depth.sell_orders)
                mm_vol = self.macaron_pos_limit - abs(pos)
                if mm_vol > 0:
                    result.setdefault("MAGNIFICENT_MACARONS", []).append(
                        Order("MAGNIFICENT_MACARONS", best_bid, mm_vol))
                    result["MAGNIFICENT_MACARONS"].append(
                        Order("MAGNIFICENT_MACARONS", best_ask, -mm_vol))

            conv_obs = state.observations.conversionObservations.get("MAGNIFICENT_MACARONS")
            if conv_obs:
                fp = (
                    self.weights["bidPrice"]    * conv_obs.bidPrice
                  + self.weights["askPrice"]    * conv_obs.askPrice
                  + self.weights["transportFees"]* conv_obs.transportFees
                  + self.weights["exportTariff"] * conv_obs.exportTariff
                  + self.weights["importTariff"] * conv_obs.importTariff
                  + self.weights["sugarPrice"]   * conv_obs.sugarPrice
                  + self.weights["sunlight"]     * conv_obs.sunlightIndex
                  + self.intercept
                )
                avg_pnl = sum(cp_scores.values()) / len(cp_scores) if cp_scores else 0.0
                mult = 1.0 + max(-0.5, min(0.5, avg_pnl / 1000.0))
                cap = int(round(self.base_conv * mult))

                buy_cost = conv_obs.askPrice + conv_obs.transportFees + conv_obs.importTariff
                sell_rev = conv_obs.bidPrice - (conv_obs.transportFees + conv_obs.exportTariff)

                if buy_cost < fp and pos > -self.macaron_pos_limit:
                    conversions = -min(cap, pos + self.macaron_pos_limit)
                    bought_last = False

                elif sell_rev > fp and pos < self.macaron_pos_limit:
                    conversions = min(cap, self.macaron_pos_limit - pos)
                    bought_last = True

                elif pos > 0:
                    conversions = min(cap, pos)
                elif pos < 0:
                    conversions = -min(cap, -pos)

        traderData = json.dumps({
            "cp_scores": cp_scores,
            "bought_last": bought_last
        })
        return result, conversions, traderData
