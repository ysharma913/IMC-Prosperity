from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

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
            
            # Check if the current product is the 'BANANAS' product, only then run the order logic
            if product == 'BANANAS':

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]

                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                acceptable_price = BANANA_VALUE - 108

                # If statement checks if there are any SELL orders in the PEARLS market
                if len(order_depth.sell_orders) > 0:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_volume = order_depth.sell_orders[best_ask]

                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        print("BUY", str(best_ask_volume) + "x", best_ask)
                        orders.append(Order(product, best_ask, best_ask_volume))

                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_volume = order_depth.buy_orders[best_bid]
                    if best_bid > acceptable_price:
                        print("SELL", str(-best_bid_volume) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_volume))

                result[product] = orders


            if product == 'PEARLS':
                order_depth = state.order_depths[product]
                orders = []

                # Pearls are valued at 10000, and they are low-risk/stable
                acceptable_price = PEARL_VALUE

                # Checking if there are sell orders
                if len(order_depth.sell_orders) > 0:
                    for ask in order_depth.sell_orders.keys():
                        if ask < acceptable_price:
                            ask_vol = order_depth.sell_orders[ask]
                            print("BUY", str(ask_vol) + "x", ask)
                            orders.append(Order(product, ask, ask_vol))
                
                # Checking if there are buy orders
                if len(order_depth.buy_orders) > 0:
                    for bid in order_depth.buy_orders.keys():
                        if bid >= acceptable_price:
                            bid_vol = order_depth.buy_orders[bid]
                            print("SELL", str(-bid_vol) + "x", bid)
                            orders.append(Order(product, bid, -bid_vol))

                result[product] = orders

        return result
