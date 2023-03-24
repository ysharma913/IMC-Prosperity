from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order

POS_LIMIT = 20

class Trader:

    def spreadOrders(self, product, buyOffer, sellOffer, maxBuy, maxSell, orders, bought, sold):
        if not bought:
            print("BUY", str(-maxBuy) + "x", buyOffer, end = "|")
            orders.append(Order(product, buyOffer, maxBuy))

        if not sold:
            print("SELL", str(maxSell) + "x", sellOffer, end = "|")
            orders.append(Order(product, sellOffer, -maxSell))


    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        lastPrices = {'PEARLS': 10_000, 'BANANAS': 5000}

        result = {}
        for product in state.order_depths.keys():
            
            if product == 'BANANAS':
                pos = state.position.get(product, 0)
                max_buy = min(POS_LIMIT - pos, POS_LIMIT)
                max_sell = min(abs(-POS_LIMIT - pos), POS_LIMIT)
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []
                bid = max(order_depth.buy_orders.keys())
                ask = min(order_depth.sell_orders.keys())
                avg_price = (bid+ask)/2
                bought, sold = False, False
                for buyPrice in sorted(order_depth.sell_orders):
                    if buyPrice < avg_price:
                        volume = min(max_buy, abs(order_depth.sell_orders[buyPrice]))
                        max_buy -= volume

                        print("BUY", str(-volume) + "x", buyPrice, end = "|")
                        orders.append(Order(product, buyPrice, volume))
                        bought = True
                
                for sellPrice in sorted(order_depth.buy_orders, reverse=True):
                    if sellPrice > avg_price:
                        volume = min(max_sell, abs(order_depth.buy_orders[buyPrice]))
                        max_sell -= volume

                        print("SELL", str(volume) + "x", sellPrice, end = "|")
                        orders.append(Order(product, sellPrice, -volume))
                        sold = True
                
                if not bought and max_buy > 0:
                    less = (max_buy+9)//10
                    for i in range(int(avg_price)-less - 3, int(avg_price) - 3):
                        vol = 10 if max_buy >= 10 else max_buy
                        print("BUY", str(-vol) + "x", i, end = "|")
                        orders.append(Order(product, i, vol))
                        max_buy -= vol
                if not sold and max_sell > 0:
                    less = (max_sell+9)//10
                    for i in range(int(avg_price)+less + 3, int(avg_price) + 3, -1):
                        vol = 10 if max_sell >= 10 else max_sell
                        print("SELL", str(vol) + "x", i, end= "|")
                        orders.append(Order(product, i, -vol))
                        max_sell -= vol
                

                lastPrices[product] = avg_price
                result[product] = orders
                print()
                
            elif product == 'PEARLS':
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
                    for i in range(10000-less - 3, 10000 - 3):
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
                    for i in range(10000+less + 3, 10000 + 3, -1):
                        vol = 10 if max_sell >= 10 else max_sell
                        print("SELL", str(vol) + "x", i, end= "|")
                        orders.append(Order(product, i, -vol))
                        max_sell -= vol
                # Add all the above orders to the result dict
                result[product] = orders
                print()
        
        return result
