from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order
import operator
from collections import defaultdict

class Trader:

    last_exp = {}
    last_slope = {}
    exps = defaultdict(list)
    def _get_expected_total(self, orders: Dict[int, int]) -> Tuple[int]:
        expected_val = 0
        total = 0

        for price in orders.keys():
            expected_val += price * abs(orders[price])
            total += abs(orders[price])

        return expected_val, total


    def get_expected_price(self, state: TradingState) -> Dict[str, float]:

      ret: Dict[str, float] = {}
      for product in state.order_depths.keys():              
        expected_val = 0
        total = 0

        buy_orders = state.order_depths[product].buy_orders
        sell_orders = state.order_depths[product].sell_orders
        print(buy_orders)
        print(sell_orders)
        
        exp_buy, total_buy = self._get_expected_total(state.order_depths[product].buy_orders)
        exp_sell, total_sell = self._get_expected_total(state.order_depths[product].sell_orders)

        expected_val = exp_buy + exp_sell
        total = total_buy  + total_sell

        expected_val_total = expected_val/total if total != 0 else (self.last_slope[product]if product in self.last_slope else 0)

        expected_val_buy = exp_buy/total_buy if total_buy != 0 else 0
        expected_val_sell = exp_sell/total_sell if total_sell != 0 else float('inf')
        
        ret[product] = (expected_val_total, expected_val_buy, expected_val_sell)

      return ret
    
    def do_order(self, bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
        reverse = False
        if trade_made == "SELL":
            reverse = True
        orders_sorted = sorted(bot_orders.keys(), reverse = reverse)
        for prices in orders_sorted:
            if operator(prices, acceptable_price):
                volume = abs(bot_orders[prices])
                vol_to_trade = min(volume, max_vol)
                max_vol -= vol_to_trade
                # In case the lowest ask is lower than our fair value,
                # This presents an opportunity for us to buy cheaply
                # The code below therefore sends a BUY order at the price level of the ask,
                # with the same quantity
                # We expect this order to trade with the sell order
                print(trade_made, str(vol_to_trade) + "x", prices)
                if trade_made == "BUY":
                    order_lst.append(Order(product, prices, vol_to_trade))
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -vol_to_trade))
            else: 
                break
            if max_vol <= 0:
                break

    
    def opposite_signs(self, x, y):
        return (x < 0) if (y >= 0) else (y < 0)
    
    def do_flood(self, trade_made, price , max_vol, product, order_lst):
        if trade_made == "SELL":
            max_vol *= -1
        order_lst.append(Order(product, price, max_vol))



    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        print(state.order_depths)
        result = {}
        expected_val_dict = self.get_expected_price(state)
       

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            
            if product == 'BANANAS':
                pos = state.position.get(product, 0)
                max_buy = 20 - pos
                max_sell= abs(-20 - pos)
                expected_val_tup = expected_val_dict[product]
                expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []
            
                if product in self.last_exp:
                    
                    last_exp = self.last_exp[product]
                    slope = (expected_val_total - last_exp)/1
                    last_slope = self.last_slope[product]

                    max_ask = max(order_depth.sell_orders.keys())
                    min_bid = min(order_depth.buy_orders.keys())

                    bid_ask = max_ask - min_bid
                    stretch = bid_ask * 1/5
                    sell_flood_price = max_ask - stretch 
                    buy_flood_price = min_bid + stretch



                    # why check slopes, just check if last_exp < this_exp, its going down so sell, if > then going up so buy
                    if self.opposite_signs(slope, last_slope):
                        print("expected_val",  expected_val_total)
                        print("expected_val_buy", expected_val_buy)
                        print("expected_val_sell", expected_val_sell)
                        print("slope: ", slope)
                        print("slope: ", slope)
                        # slope changed from neg to pos, buy
                        if slope > last_slope:
                            self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= expected_val_sell, trade_made="BUY", product=product, order_lst = orders)

                        elif slope < last_slope:
                            self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= expected_val_buy, trade_made="SELL", product=product, order_lst = orders)

                    # flood asks, we have bought!!
                    elif slope < 0:
                        self.do_flood(trade_made="SELL", price = sell_flood_price, max_vol = 2, product=product, order_lst = orders)

                    elif slope > 0:
                        self.do_flood(trade_made="BUY", price = buy_flood_price, max_vol = 2, product=product, order_lst = orders)

                    result[product] = orders
                    self.last_slope[product] = slope
                else:
                    self.last_slope[product] = 0

                
                self.last_exp[product] = expected_val_total
                print(result[product])
                self.exps[product].append(expected_val_total)
        print(self.exps)
        return result
