
from datamodel import OrderDepth, TradingState, Order
from typing import List
import numpy as np
import jsonpickle
import math

def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))

def Black_Scholes(r: float, S: float, K: float, T: float, Sig: float, Option_Type: str = "call") -> float:
    D1 = (math.log(S / K) + (r + 0.5 * Sig**2) * T) / (Sig * math.sqrt(T))
    D2 = D1 - Sig * math.sqrt(T)
    if Option_Type == "call":
        Price = S * norm_cdf(D1) - K * math.exp(-r * T) * norm_cdf(D2)
    elif Option_Type == "put":
        Price = K * math.exp(-r * T) * norm_cdf(-D2) - S * norm_cdf(-D1)
    else:
        raise ValueError("Invalid Option Type")
    return Price

class Trader:
    def __init__(self):
        self.deviation_threshold = 0.05  
        self.exit_threshold = 0.02         
        self.trade_size = 10

        self.pos_limit_voucher = 200

        self.vouchers = {
            "VOLCANIC_ROCK_VOUCHER_9500": 9500,
            "VOLCANIC_ROCK_VOUCHER_9750": 9750,
            "VOLCANIC_ROCK_VOUCHER_10000": 10000,
            "VOLCANIC_ROCK_VOUCHER_10250": 10250,
            "VOLCANIC_ROCK_VOUCHER_10500": 10500
        }
        self.TTE = 4    
        self.r = 0.0    
        self.Sig = 0.2  

    def run(self, state: TradingState) -> tuple[dict, int, str]:
        result = {}
        traderDataDict = {}
        conversions = 1

        if "VOLCANIC_ROCK" not in state.order_depths:
            return result, conversions, ""
        volr_depth = state.order_depths["VOLCANIC_ROCK"]
        if not volr_depth.buy_orders or not volr_depth.sell_orders:
            return result, conversions, ""
        volr_bid = max(volr_depth.buy_orders.keys())
        volr_ask = min(volr_depth.sell_orders.keys())
        St = (volr_bid + volr_ask) / 2

        orders = {}
        m_list = []
        v_list = []
        voucher_data = {}  
        
        for voucher, K in self.vouchers.items():
            if voucher in state.order_depths:
                vou_depth = state.order_depths[voucher]
                if vou_depth.buy_orders and vou_depth.sell_orders:
                    best_bid = max(vou_depth.buy_orders.keys())
                    best_ask = min(vou_depth.sell_orders.keys())
                    Vt = (best_bid + best_ask) / 2
                    voucher_data[voucher] = {"best_bid": best_bid, "best_ask": best_ask, "Vt": Vt}
                    m_t = math.log(K / St) / math.sqrt(self.TTE)
                    v_t = Black_Scholes(self.r, St, K, self.TTE, self.Sig, Option_Type="call")
                    m_list.append(m_t)
                    v_list.append(v_t)
        if len(m_list) < 2:
            return result, conversions, jsonpickle.encode({"message": "Not enough voucher data"})
        
        coeffs = np.polyfit(m_list, v_list, 2)
        base_IV = coeffs[-1]
        
        orders = {}
        for voucher, K in self.vouchers.items():
            if voucher not in voucher_data:
                continue
            data = voucher_data[voucher]
            Vt = data["Vt"]
            m_t = math.log(K / St) / math.sqrt(self.TTE)
            v_t = Black_Scholes(self.r, St, K, self.TTE, self.Sig, Option_Type="call")
            fitted_v = coeffs[0] * m_t**2 + coeffs[1] * m_t + coeffs[2]
            deviation = Vt - fitted_v  
            pos = state.position.get(voucher, 0)
            orders_voucher: List[Order] = []
            # Reversed trading logic: 
            # (Normally, if deviation > threshold, we go short; now we go long, and vice versa.)
            if deviation > self.deviation_threshold:
                best_ask = min(state.order_depths[voucher].sell_orders.keys())
                available = abs(state.order_depths[voucher].sell_orders.get(best_ask, 0))
                buy_qty = min(self.trade_size, available, self.pos_limit_voucher - pos)
                if buy_qty > 0:
                    orders_voucher.append(Order(voucher, best_ask, buy_qty))
            elif deviation < -self.deviation_threshold:
                best_bid = max(state.order_depths[voucher].buy_orders.keys())
                available = state.order_depths[voucher].buy_orders.get(best_bid, 0)
                sell_qty = min(self.trade_size, available, pos + self.pos_limit_voucher)
                if sell_qty > 0:
                    orders_voucher.append(Order(voucher, best_bid, -sell_qty))
            elif abs(deviation) < self.exit_threshold:
                if pos != 0:
                    if pos > 0:
                        best_bid = max(state.order_depths[voucher].buy_orders.keys())
                        qty = min(pos, state.order_depths[voucher].buy_orders.get(best_bid, 0))
                        if qty > 0:
                            orders_voucher.append(Order(voucher, best_bid, -qty))
                    else:
                        best_ask = min(state.order_depths[voucher].sell_orders.keys())
                        qty = min(abs(pos), abs(state.order_depths[voucher].sell_orders.get(best_ask, 0)))
                        if qty > 0:
                            orders_voucher.append(Order(voucher, best_ask, qty))
            if orders_voucher:
                orders[voucher] = orders_voucher
            traderDataDict[voucher] = {
                "Vt": Vt,
                "theoretical_price": fitted_v,
                "deviation": deviation
            }
        traderDataDict["fitting"] = {"coeffs": coeffs.tolist(), "base_IV": base_IV, "St": St, "TTE": self.TTE}

        for voucher, ord_list in orders.items():
            result[voucher] = ord_list

        return result, conversions, jsonpickle.encode(traderDataDict)
