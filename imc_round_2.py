
from datamodel import OrderDepth, TradingState, Order
from typing import List
import numpy as np
import jsonpickle

class Trader:
    def __init__(self):
        self.upper_threshold = 0.1 
        self.lower_threshold = -0.1 
        self.exit_threshold = 0.05 
        self.trade_size = 10

        self.pos_limit_PB2 = 100      # PICNIC_BASKET2
        self.pos_limit_SQUID = 50     # SQUID_INK
        self.pos_limit_CROISSANTS = 250
        self.pos_limit_PB1 = 60       # PICNIC_BASKET1
        self.pos_limit_DJEMBES = 60
        self.pos_limit_JAMS = 350

    def normalize_pair(self, val_a: float, val_b: float) -> (float, float):
        mn = min(val_a, val_b)
        mx = max(val_a, val_b)
        if mx - mn == 0:
            return 0.5, 0.5
        norm_a = (val_a - mn) / (mx - mn)
        norm_b = (val_b - mn) / (mx - mn)
        return norm_a, norm_b
    
    def merge_orders(self, result: dict, orders: List[Order], symbol: str):
        if orders:
            result[symbol] = result.get(symbol, []) + orders
    
    def run(self, state: TradingState) -> tuple[dict, int, str]:
        result = {}
        traderDataDict = {}
        conversions = 1
    
        # CODE 1: PICNIC_BASKET2 - SQUID_INK
        if "PICNIC_BASKET2" in state.order_depths and "SQUID_INK" in state.order_depths:
            pb2_depth = state.order_depths["PICNIC_BASKET2"]
            squid_depth = state.order_depths["SQUID_INK"]
            if pb2_depth.buy_orders and pb2_depth.sell_orders and squid_depth.buy_orders and squid_depth.sell_orders:
                pb2_best_bid = max(pb2_depth.buy_orders.keys())
                pb2_best_ask = min(pb2_depth.sell_orders.keys())
                mid_PB2 = (pb2_best_bid + pb2_best_ask) / 2
    
                squid_best_bid = max(squid_depth.buy_orders.keys())
                squid_best_ask = min(squid_depth.sell_orders.keys())
                mid_SQUID = (squid_best_bid + squid_best_ask) / 2
    
                norm_PB2, norm_SQUID = self.normalize_pair(mid_PB2, mid_SQUID)
                spread = norm_PB2 - norm_SQUID
    
                pos_PB2 = state.position.get("PICNIC_BASKET2", 0)
                pos_SQUID = state.position.get("SQUID_INK", 0)
    
                orders_PB2: List[Order] = []
                orders_SQUID: List[Order] = []
    
                if spread > self.upper_threshold:
                    available_pb2 = pb2_depth.buy_orders.get(pb2_best_bid, 0)
                    sell_qty = min(self.trade_size, available_pb2, pos_PB2 + self.pos_limit_PB2)
                    if sell_qty > 0:
                        orders_PB2.append(Order("PICNIC_BASKET2", pb2_best_bid, -sell_qty))
                    available_sq = abs(squid_depth.sell_orders.get(squid_best_ask, 0))
                    buy_qty = min(self.trade_size, available_sq, self.pos_limit_SQUID - pos_SQUID)
                    if buy_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_ask, buy_qty))
                elif spread < self.lower_threshold:
                    available_pb2 = abs(pb2_depth.sell_orders.get(pb2_best_ask, 0))
                    buy_qty = min(self.trade_size, available_pb2, self.pos_limit_PB2 - pos_PB2)
                    if buy_qty > 0:
                        orders_PB2.append(Order("PICNIC_BASKET2", pb2_best_ask, buy_qty))
                    available_sq = squid_depth.buy_orders.get(squid_best_bid, 0)
                    sell_qty = min(self.trade_size, available_sq, pos_SQUID + self.pos_limit_SQUID)
                    if sell_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -sell_qty))
                elif abs(spread) < self.exit_threshold:
                    if pos_PB2 != 0:
                        if pos_PB2 > 0:
                            qty = min(pos_PB2, pb2_depth.buy_orders.get(pb2_best_bid, 0))
                            if qty > 0:
                                orders_PB2.append(Order("PICNIC_BASKET2", pb2_best_bid, -qty))
                        else:
                            qty = min(abs(pos_PB2), abs(pb2_depth.sell_orders.get(pb2_best_ask, 0)))
                            if qty > 0:
                                orders_PB2.append(Order("PICNIC_BASKET2", pb2_best_ask, qty))
                    if pos_SQUID != 0:
                        if pos_SQUID > 0:
                            qty = min(pos_SQUID, squid_depth.buy_orders.get(squid_best_bid, 0))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -qty))
                        else:
                            qty = min(abs(pos_SQUID), abs(squid_depth.sell_orders.get(squid_best_ask, 0)))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_ask, qty))
                self.merge_orders(result, orders_PB2, "PICNIC_BASKET2")
                self.merge_orders(result, orders_SQUID, "SQUID_INK")
                traderDataDict["pair_PB2_SQUID"] = {
                    "normalized_PB2": norm_PB2,
                    "normalized_SQUID": norm_SQUID,
                    "spread": spread
                }

        # CODE 2: CROISSANTS - PICNIC_BASKET1
        if "CROISSANTS" in state.order_depths and "PICNIC_BASKET1" in state.order_depths:
            croiss_depth = state.order_depths["CROISSANTS"]
            pb1_depth = state.order_depths["PICNIC_BASKET1"]
            if croiss_depth.buy_orders and croiss_depth.sell_orders and pb1_depth.buy_orders and pb1_depth.sell_orders:
                croiss_best_bid = max(croiss_depth.buy_orders.keys())
                croiss_best_ask = min(croiss_depth.sell_orders.keys())
                mid_CROISSANTS = (croiss_best_bid + croiss_best_ask) / 2
    
                pb1_best_bid = max(pb1_depth.buy_orders.keys())
                pb1_best_ask = min(pb1_depth.sell_orders.keys())
                mid_PB1 = (pb1_best_bid + pb1_best_ask) / 2
    
                norm_CROISSANTS, norm_PB1 = self.normalize_pair(mid_CROISSANTS, mid_PB1)
                spread = norm_CROISSANTS - norm_PB1
    
                pos_CROISSANTS = state.position.get("CROISSANTS", 0)
                pos_PB1 = state.position.get("PICNIC_BASKET1", 0)
    
                orders_CROISSANTS: List[Order] = []
                orders_PB1: List[Order] = []
    
                if spread > self.upper_threshold:
                    available_croiss = croiss_depth.buy_orders.get(croiss_best_bid, 0)
                    sell_qty = min(self.trade_size, available_croiss, pos_CROISSANTS + self.pos_limit_CROISSANTS)
                    if sell_qty > 0:
                        orders_CROISSANTS.append(Order("CROISSANTS", croiss_best_bid, -sell_qty))
                    available_pb1 = abs(pb1_depth.sell_orders.get(pb1_best_ask, 0))
                    buy_qty = min(self.trade_size, available_pb1, self.pos_limit_PB1 - pos_PB1)
                    if buy_qty > 0:
                        orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_ask, buy_qty))
                elif spread < self.lower_threshold:
                    available_croiss = abs(croiss_depth.sell_orders.get(croiss_best_ask, 0))
                    buy_qty = min(self.trade_size, available_croiss, self.pos_limit_CROISSANTS - pos_CROISSANTS)
                    if buy_qty > 0:
                        orders_CROISSANTS.append(Order("CROISSANTS", croiss_best_ask, buy_qty))
                    available_pb1 = pb1_depth.buy_orders.get(pb1_best_bid, 0)
                    sell_qty = min(self.trade_size, available_pb1, pos_PB1 + self.pos_limit_PB1)
                    if sell_qty > 0:
                        orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_bid, -sell_qty))
                elif abs(spread) < self.exit_threshold:
                    if pos_CROISSANTS != 0:
                        if pos_CROISSANTS > 0:
                            qty = min(pos_CROISSANTS, croiss_depth.buy_orders.get(croiss_best_bid, 0))
                            if qty > 0:
                                orders_CROISSANTS.append(Order("CROISSANTS", croiss_best_bid, -qty))
                        else:
                            qty = min(abs(pos_CROISSANTS), abs(croiss_depth.sell_orders.get(croiss_best_ask, 0)))
                            if qty > 0:
                                orders_CROISSANTS.append(Order("CROISSANTS", croiss_best_ask, qty))
                    if pos_PB1 != 0:
                        if pos_PB1 > 0:
                            qty = min(pos_PB1, pb1_depth.buy_orders.get(pb1_best_bid, 0))
                            if qty > 0:
                                orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_bid, -qty))
                        else:
                            qty = min(abs(pos_PB1), abs(pb1_depth.sell_orders.get(pb1_best_ask, 0)))
                            if qty > 0:
                                orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_ask, qty))
                self.merge_orders(result, orders_CROISSANTS, "CROISSANTS")
                self.merge_orders(result, orders_PB1, "PICNIC_BASKET1")
                traderDataDict["pair_CROISSANTS_PB1"] = {
                    "normalized_CROISSANTS": norm_CROISSANTS,
                    "normalized_PB1": norm_PB1,
                    "spread": spread
                }
    
    
        # CODE 4: DJEMBES - SQUID_INK
        if "DJEMBES" in state.order_depths and "SQUID_INK" in state.order_depths:
            djemb_depth = state.order_depths["DJEMBES"]
            squid_depth = state.order_depths["SQUID_INK"]
            if djemb_depth.buy_orders and djemb_depth.sell_orders and squid_depth.buy_orders and squid_depth.sell_orders:
                djemb_best_bid = max(djemb_depth.buy_orders.keys())
                djemb_best_ask = min(djemb_depth.sell_orders.keys())
                mid_DJEMBES = (djemb_best_bid + djemb_best_ask) / 2
    
                squid_best_bid = max(squid_depth.buy_orders.keys())
                squid_best_ask = min(squid_depth.sell_orders.keys())
                mid_SQUID = (squid_best_bid + squid_best_ask) / 2
    
                norm_DJEMBES, norm_SQUID = self.normalize_pair(mid_DJEMBES, mid_SQUID)
                spread = norm_DJEMBES - norm_SQUID
    
                pos_DJEMBES = state.position.get("DJEMBES", 0)
                pos_SQUID = state.position.get("SQUID_INK", 0)
    
                orders_DJEMBES: List[Order] = []
                orders_SQUID: List[Order] = []
    
                if spread > self.upper_threshold:
                    available_djemb = djemb_depth.buy_orders.get(djemb_best_bid, 0)
                    sell_qty = min(self.trade_size, available_djemb, pos_DJEMBES + self.pos_limit_DJEMBES)
                    if sell_qty > 0:
                        orders_DJEMBES.append(Order("DJEMBES", djemb_best_bid, -sell_qty))
                    available_sq = abs(squid_depth.sell_orders.get(squid_best_ask, 0))
                    buy_qty = min(self.trade_size, available_sq, self.pos_limit_SQUID - pos_SQUID)
                    if buy_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_ask, buy_qty))
                elif spread < self.lower_threshold:
                    available_djemb = abs(djemb_depth.sell_orders.get(djemb_best_ask, 0))
                    buy_qty = min(self.trade_size, available_djemb, self.pos_limit_DJEMBES - pos_DJEMBES)
                    if buy_qty > 0:
                        orders_DJEMBES.append(Order("DJEMBES", djemb_best_ask, buy_qty))
                    available_sq = squid_depth.buy_orders.get(squid_best_bid, 0)
                    sell_qty = min(self.trade_size, available_sq, pos_SQUID + self.pos_limit_SQUID)
                    if sell_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -sell_qty))
                elif abs(spread) < self.exit_threshold:
                    if pos_DJEMBES != 0:
                        if pos_DJEMBES > 0:
                            qty = min(pos_DJEMBES, djemb_depth.buy_orders.get(djemb_best_bid, 0))
                            if qty > 0:
                                orders_DJEMBES.append(Order("DJEMBES", djemb_best_bid, -qty))
                        else:
                            qty = min(abs(pos_DJEMBES), abs(djemb_depth.sell_orders.get(djemb_best_ask, 0)))
                            if qty > 0:
                                orders_DJEMBES.append(Order("DJEMBES", djemb_best_ask, qty))
                    if pos_SQUID != 0:
                        if pos_SQUID > 0:
                            qty = min(pos_SQUID, squid_depth.buy_orders.get(squid_best_bid, 0))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -qty))
                        else:
                            qty = min(abs(pos_SQUID), abs(squid_depth.sell_orders.get(squid_best_ask, 0)))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_ask, qty))
                self.merge_orders(result, orders_DJEMBES, "DJEMBES")
                self.merge_orders(result, orders_SQUID, "SQUID_INK")
                traderDataDict["pair_DJEMBES_SQUID"] = {
                    "normalized_DJEMBES": norm_DJEMBES,
                    "normalized_SQUID": norm_SQUID,
                    "spread": spread
                }
    
        # CODE 7: PICNIC_BASKET1 - SQUID_INK
        if "PICNIC_BASKET1" in state.order_depths and "SQUID_INK" in state.order_depths:
            pb1_depth = state.order_depths["PICNIC_BASKET1"]
            squid_depth = state.order_depths["SQUID_INK"]
            if pb1_depth.buy_orders and pb1_depth.sell_orders and squid_depth.buy_orders and squid_depth.sell_orders:
                pb1_best_bid = max(pb1_depth.buy_orders.keys())
                pb1_best_ask = min(pb1_depth.sell_orders.keys())
                mid_PB1 = (pb1_best_bid + pb1_best_ask) / 2
    
                squid_best_bid = max(squid_depth.buy_orders.keys())
                squid_best_ask = min(squid_depth.sell_orders.keys())
                mid_SQUID = (squid_best_bid + squid_best_ask) / 2
    
                norm_PB1, norm_SQUID = self.normalize_pair(mid_PB1, mid_SQUID)
                spread = norm_PB1 - norm_SQUID
    
                pos_PB1 = state.position.get("PICNIC_BASKET1", 0)
                pos_SQUID = state.position.get("SQUID_INK", 0)
    
                orders_PB1: List[Order] = []
                orders_SQUID: List[Order] = []
    
                if spread > self.upper_threshold:
                    available_pb1 = pb1_depth.buy_orders.get(pb1_best_bid, 0)
                    sell_qty = min(self.trade_size, available_pb1, pos_PB1 + self.pos_limit_PB1)
                    if sell_qty > 0:
                        orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_bid, -sell_qty))
                    available_sq = abs(squid_depth.sell_orders.get(squid_best_ask, 0))
                    buy_qty = min(self.trade_size, available_sq, self.pos_limit_SQUID - pos_SQUID)
                    if buy_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_ask, buy_qty))
                elif spread < self.lower_threshold:
                    available_pb1 = abs(pb1_depth.sell_orders.get(pb1_best_ask, 0))
                    buy_qty = min(self.trade_size, available_pb1, self.pos_limit_PB1 - pos_PB1)
                    if buy_qty > 0:
                        orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_ask, buy_qty))
                    available_sq = squid_depth.buy_orders.get(squid_best_bid, 0)
                    sell_qty = min(self.trade_size, available_sq, pos_SQUID + self.pos_limit_SQUID)
                    if sell_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -sell_qty))
                elif abs(spread) < self.exit_threshold:
                    if pos_PB1 != 0:
                        if pos_PB1 > 0:
                            qty = min(pos_PB1, pb1_depth.buy_orders.get(pb1_best_bid, 0))
                            if qty > 0:
                                orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_bid, -qty))
                        else:
                            qty = min(abs(pos_PB1), abs(pb1_depth.sell_orders.get(pb1_best_ask, 0)))
                            if qty > 0:
                                orders_PB1.append(Order("PICNIC_BASKET1", pb1_best_ask, qty))
                    if pos_SQUID != 0:
                        if pos_SQUID > 0:
                            qty = min(pos_SQUID, squid_depth.buy_orders.get(squid_best_bid, 0))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -qty))
                        else:
                            qty = min(abs(pos_SQUID), abs(squid_depth.sell_orders.get(squid_best_ask, 0)))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_ask, qty))
                self.merge_orders(result, orders_PB1, "PICNIC_BASKET1")
                self.merge_orders(result, orders_SQUID, "SQUID_INK")
                traderDataDict["pair_PB1_SQUID"] = {
                    "normalized_PB1": norm_PB1,
                    "normalized_SQUID": norm_SQUID,
                    "spread": spread
                }
    
        # CODE 8: JAMS - SQUID_INK
        if "JAMS" in state.order_depths and "SQUID_INK" in state.order_depths:
            jams_depth = state.order_depths["JAMS"]
            squid_depth = state.order_depths["SQUID_INK"]
            if jams_depth.buy_orders and jams_depth.sell_orders and squid_depth.buy_orders and squid_depth.sell_orders:
                jams_best_bid = max(jams_depth.buy_orders.keys())
                jams_best_ask = min(jams_depth.sell_orders.keys())
                mid_JAMS = (jams_best_bid + jams_best_ask) / 2
    
                squid_best_bid = max(squid_depth.buy_orders.keys())
                squid_best_ask = min(squid_depth.sell_orders.keys())
                mid_SQUID = (squid_best_bid + squid_best_ask) / 2
    
                norm_JAMS, norm_SQUID = self.normalize_pair(mid_JAMS, mid_SQUID)
                spread = norm_JAMS - norm_SQUID
    
                pos_JAMS = state.position.get("JAMS", 0)
                pos_SQUID = state.position.get("SQUID_INK", 0)
    
                orders_JAMS: List[Order] = []
                orders_SQUID: List[Order] = []
    
                if spread > self.upper_threshold:
                    available_jams = jams_depth.buy_orders.get(jams_best_bid, 0)
                    sell_qty = min(self.trade_size, available_jams, pos_JAMS + self.pos_limit_JAMS)
                    if sell_qty > 0:
                        orders_JAMS.append(Order("JAMS", jams_best_bid, -sell_qty))
                    available_sq = abs(squid_depth.sell_orders.get(squid_best_ask, 0))
                    buy_qty = min(self.trade_size, available_sq, self.pos_limit_SQUID - pos_SQUID)
                    if buy_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_ask, buy_qty))
                elif spread < self.lower_threshold:
                    available_jams = abs(jams_depth.sell_orders.get(jams_best_ask, 0))
                    buy_qty = min(self.trade_size, available_jams, self.pos_limit_JAMS - pos_JAMS)
                    if buy_qty > 0:
                        orders_JAMS.append(Order("JAMS", jams_best_ask, buy_qty))
                    available_sq = squid_depth.buy_orders.get(squid_best_bid, 0)
                    sell_qty = min(self.trade_size, available_sq, pos_SQUID + self.pos_limit_SQUID)
                    if sell_qty > 0:
                        orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -sell_qty))
                elif abs(spread) < self.exit_threshold:
                    if pos_JAMS != 0:
                        if pos_JAMS > 0:
                            qty = min(pos_JAMS, jams_depth.buy_orders.get(jams_best_bid, 0))
                            if qty > 0:
                                orders_JAMS.append(Order("JAMS", jams_best_bid, -qty))
                        else:
                            qty = min(abs(pos_JAMS), abs(jams_depth.sell_orders.get(jams_best_ask, 0)))
                            if qty > 0:
                                orders_JAMS.append(Order("JAMS", jams_best_ask, qty))
                    if pos_SQUID != 0:
                        if pos_SQUID > 0:
                            qty = min(pos_SQUID, squid_depth.buy_orders.get(squid_best_bid, 0))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_bid, -qty))
                        else:
                            qty = min(abs(pos_SQUID), abs(squid_depth.sell_orders.get(squid_best_ask, 0)))
                            if qty > 0:
                                orders_SQUID.append(Order("SQUID_INK", squid_best_ask, qty))
                self.merge_orders(result, orders_JAMS, "JAMS")
                self.merge_orders(result, orders_SQUID, "SQUID_INK")
                traderDataDict["pair_JAMS_SQUID"] = {
                    "normalized_JAMS": norm_JAMS,
                    "normalized_SQUID": norm_SQUID,
                    "spread": spread
                }
    
        # End of all strategy blocks.
    
        traderData = jsonpickle.encode(traderDataDict)
        return result, conversions, traderData
