from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import operator

class Trader:
    
    def do_order(self, bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
        orders_sorted = sorted(bot_orders.keys())
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
                print(trade_made, str(volume) + "x", prices, end = "|")
                if trade_made == "BUY":
                    order_lst.append(Order(product, prices,-volume))
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -volume))
            else: 
                break
            if max_vol <= 0:
                break

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}

        # Values of product in market
        PEARL_VALUE = 10000
        BANANA_VALUE = 5000

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            pos = state.position.get(product, 0)
            max_buy = 20 - pos
            max_sell = abs(-20 - pos)
            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':
         
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                acceptable_price = BANANA_VALUE - 108

                # If statement checks if there are any SELL orders in the PEARLS market
                self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= acceptable_price, trade_made="BUY", product=product, order_lst = orders)

                self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= acceptable_price, trade_made="SELL", product=product, order_lst = orders)

                result[product] = orders

            if product == 'PEARLS':
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Pearls are valued at 10000, and they are low-risk/stable
                acceptable_price = PEARL_VALUE

                 # If statement checks if there are any SELL orders in the PEARLS market
                self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= acceptable_price, trade_made="BUY", product=product, order_lst = orders)

                self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= acceptable_price, trade_made="SELL", product=product, order_lst = orders)

                result[product] = orders

        return result
