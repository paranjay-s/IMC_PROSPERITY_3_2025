from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string



class Trader:

    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths.keys():
            order_depth: OrderDepth = state.order_depths[product]
            orders: list[Order] = []

            if product in ["RAINFOREST_RESIN"]:
                # Constants
                fair_price_RR = 9999.99655
                std_price_RR = 1.4965920476507821
                acceptable_price = fair_price_RR
                position_limit = 10
                current_pos = state.position.get(product, 0)
                
                
                #Market-Making Parameters
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
    
                # Arbitrage logic
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
    
                # Market Making
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
        
        traderData = ""
        conversions = 1

        return result, conversions, traderData
