from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import operator

class Trader:

    last_exp = {}
    last_slope = {}

    def get_expected_price(self, state: TradingState) -> Dict[str, float]:

      ret: Dict[str, float] = {}
      for product in state.order_depths.keys():              
        expected_val = 0
        total = 0
        buy_orders = state.order_depths[product].buy_orders
        sell_orders = state.order_depths[product].sell_orders
        for price in buy_orders.keys():
            expected_val += price * buy_orders[price]
            total += buy_orders[price]

        for price in sell_orders.keys():
            expected_val += price * sell_orders[price]
            total += sell_orders[price]

        ret[product] = expected_val/total if total != 0 else (self.last_slope[product]if product in self.last_slope else 0)
            

      return ret
    
    def do_order(self, bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
        reverse = False
        if trade_made == "BUY":
            reverse = True
        orders_sorted = sorted(bot_orders.keys(), reverse)
        for prices in orders_sorted:
            if operator(prices, acceptable_price):
                volume = bot_orders[prices]
                vol_to_trade = min(volume, max_vol)
                max_vol -= vol_to_trade
                # In case the lowest ask is lower than our fair value,
                # This presents an opportunity for us to buy cheaply
                # The code below therefore sends a BUY order at the price level of the ask,
                # with the same quantity
                # We expect this order to trade with the sell order
                print(trade_made, str(volume) + "x", prices)
                if trade_made == "BUY":
                    order_lst.append(Order(product, prices,-volume))
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -volume))
            else: 
                break
            if max_vol <= 0:
                break

    
    def opposite_signs(self, x, y):
        return (x < 0) if (y >= 0) else (y < 0)
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        expected_val_dict = self.get_expected_price(state)

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            pos = state.position.get(product, 0)
            max_buy = min(20 - pos, 20)
            max_sell = min(abs(-20 - pos), 20)
         
            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []
            expected_val = expected_val_dict[product]
            
            if product in self.last_exp:
                
                last_exp = self.last_exp[product]
                slope = (expected_val - last_exp)/1
                last_slope = self.last_slope[product]

                if self.opposite_signs(slope, last_slope):
                    # slope changed from neg to pos, buy
                    if slope > last_slope:
                        self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= expected_val, trade_made="BUY", product=product, order_lst = orders)

                    elif slope < last_slope:
                        self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= expected_val, trade_made="SELL", product=product, order_lst = orders)

                result[product] = orders
                self.last_slope[product] = slope
            else:
                self.last_slope[product] = 0

            
            self.last_exp[product] = expected_val
            # if product == 'PEARLS':
            #     # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            #     order_depth: OrderDepth = state.order_depths[product]

            #     # Initialize the list of Orders to be sent as an empty list
            #     orders: list[Order] = []
    
            #     expected_val = expected_val_dict.get(product, slope)
            #     slope = expected_val - self.last_exp 
            #     last_slope = self.last_slope.get(product, slope)

            #     if self.opposite_signs(slope, last_slope):
            #         # slope changed from ned to pos, buy
            #         if slope > last_slope:
            #             self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= expected_val, trade_made="BUY", product=product, order_lst = orders)

            #         elif slope < last_slope:
            #             self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= expected_val, trade_made="SELL", product=product, order_lst = orders)
                
            #     result[product] = orders

        return result
