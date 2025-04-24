
from datamodel import OrderDepth, TradingState, Order
from typing import List
import numpy as np
import json
import math



class Trader:
    def __init__(self):
       # Parameters for linear regression
       self.weights = {"bidPrice": 0.48606, "askPrice" : 0.51281, "transportFees" : 0.02976754, "exportTarrif": -0.0842141, "importTarrif": -0.06292103,
                       "sugarPrice": -0.00162174, "sunlight":-0.00577173}
       self.intercept = 1.955586762815983


    def run(self, state: TradingState) -> tuple[dict, int, str]:
        result = {}
        traderDataDict = {}
        conversions = 1

        if "MAGNIFICENT_MACARONS" not in state.order_depths:
            return result, conversions, ""
        macaron_depth = state.order_depths["MAGNIFICENT_MACARONS"]
        if not macaron_depth.buy_orders or not macaron_depth.sell_orders:
            return result, conversions, ""
        
        conv_obs = state.observations.conversionObservations.get('MAGNIFICENT_MACARONS', None)
        if conv_obs is None:
            return result, 0, ""
        
        # Linear Regresssion Parameters
        bid_price_x = conv_obs.bidPrice
        ask_price_x = conv_obs.askPrice
        transport_fees = conv_obs.transportFees
        export_tarrif = conv_obs.exportTariff
        import_tarrif = conv_obs.importTariff
        sugar_price = conv_obs.sugarPrice
        sunlight_index = conv_obs.sunlightIndex

        fair_price_macaron = int(self.weights["bidPrice"] * bid_price_x + self.weights["askPrice"] * ask_price_x + self.weights["transportFees"] * transport_fees 
                                  + self.weights["exportTarrif"] * export_tarrif + self.weights["importTarrif"] * import_tarrif + self.weights["sugarPrice"] * sugar_price
                                  + self.weights["sunlight"] * sunlight_index + self.intercept)
        
        ## market making strategy
        orders: list[Order] = []
        current_pos = state.position.get("MAGNIFICENT_MACARONS", 0)
        mm_limit = 75
        if current_pos <= 0:
            volume = mm_limit + current_pos
        else:
            volume = mm_limit - current_pos
    
        my_ask_volume = -volume
        my_bid_volume = volume

        my_bid = fair_price_macaron - 1
        my_ask = fair_price_macaron + 1
                
        print(f"Market-Making MM BUY {my_bid_volume}x @ {my_bid}")
        orders.append(Order("MAGNIFICENT_MACARONS", my_bid, my_bid_volume))
        print(f"Market-Making MM SELL {-my_ask_volume}x @ {my_ask}")
        orders.append(Order("MAGNIFICENT_MACARONS", my_ask, my_ask_volume))

        result["MAGNIFICENT_MACARONS"] = orders
        
        raw = state.traderData
        if isinstance(raw, str):
            try:
                traderData = json.loads(raw)
            except json.JSONDecodeError:
                traderData = {}
        elif isinstance(raw, dict):
            traderData = raw
        else:
            traderData = {}

        pos = state.position.get("MAGNIFICENT_MACARONS", 0)

        static_conv = 10

        if pos == 0 and not traderData.get("bought_last", False):
            conversions = static_conv
            traderData["bought_last"] = True
        elif pos > 0 and traderData.get("bought_last", False):
            conversions = -pos
            traderData["bought_last"] = False
        else:
            conversions = 0

        traderData["last_position"] = pos
        traderData["last_conversion"] = conversions

        return result, conversions, json.dumps(traderData)
        
