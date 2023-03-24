from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order


class Trader:

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """

        #
        # Initialize the method output dict as an empty dict
        result = {}
        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            # Check if the current product is the 'PEARLS' product, only then run the order logic
            if product == 'PEARLS':
                
                pos = state.position.get(product, 0)
                max_buy = min(20 - pos, 20)
                max_sell = min(abs(-20 - pos), 20)
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]


                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!
                acceptable_price = 10000

                # If statement checks if there are any SELL orders in the PEARLS market
                hadBOrder = False
                sell_keys_lst = sorted(order_depth.sell_orders.keys())
                for best_ask in sell_keys_lst:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    #best_ask = min(order_depth.sell_orders.keys())
                
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        best_ask_volume = abs(order_depth.sell_orders[best_ask])
                        vol_to_trade = min(best_ask_volume, max_buy)
                        max_buy -= vol_to_trade
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(-best_ask_volume) + "x", best_ask, end = "|")
                        orders.append(Order(product, best_ask, best_ask_volume))
                        hadBOrder = True
                    else: 
                        break
                    if max_buy <= 0:
                        break
                
                if max_buy > 0 and not hadBOrder:
                    less = (max_buy+9)//10
                    for i in range(10000 - 3, 10000 - 3 - less - 1, -1):
                        vol = 10 if max_buy >= 10 else max_buy
                        print("BUY", str(-vol) + "x", i, end = "|")
                        orders.append(Order(product, i, vol))
                        max_buy -= vol

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium   
                hadSOrder = False
                buy_keys_lst = sorted(order_depth.buy_orders.keys(), reverse = True)
                for best_bid in buy_keys_lst:

                    # best_bid = max(order_depth.buy_orders.keys())

                    if best_bid > acceptable_price:
                        best_bid_volume = order_depth.buy_orders[best_bid]
                        vol_to_trade = min(best_bid_volume, max_sell)
                        max_sell -= vol_to_trade
                        print("SELL", str(vol_to_trade) + "x", best_bid, end= "|")
                        orders.append(Order(product, best_bid, -vol_to_trade))
                        hadSOrder = True
                    else:
                        break
                    if max_sell <= 0:
                        break
                
                if max_sell > 0 and not hadSOrder:
                    less = (max_sell+9)//10
                    for i in range(10000 + 3, 10000 + 3 + less):
                        vol = 10 if max_sell >= 10 else max_sell
                        print("SELL", str(vol) + "x", i, end= "|")
                        orders.append(Order(product, i, -vol))
                        max_sell -= vol
                # Add all the above orders to the result dict
                result[product] = orders
                print()

                # Return the dict of orders
                # These possibly contain buy or sell orders for PEARLS
                # Depending on the logic above
        return result
