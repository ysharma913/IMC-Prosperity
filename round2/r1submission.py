from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Symbol, Trade, Listing
import operator
from collections import defaultdict, deque
import pandas as pd
import numpy as np
class Trader:

    current_iter = 0
    cache = list()

    # past_averages


    window_size = 5
    z_window_size = 5

    def z_score(self, x: float):
        last_window = np.array(self.cache[-self.z_window_size - 1: -1])

        return (x - last_window.mean())/last_window.std()

    def rolling_mean(self):
      return np.array(self.cache[-self.z_window_size - 1:-1]).mean()

    def _best_fit_line(self, pairs: pd.DataFrame = None):

        x,y = zip(*pairs)
        x,y = np.array(x), np.array(y)

        # assert len(pairs) == 2763
        return np.poly1d(np.polyfit(x, y, 1))


    def _get_expected_total(self, orders: Dict[int, int]) -> Tuple[int]:
        expected_val = 0
        total = 0

        for price in orders.keys():
            expected_val += price * abs(orders[price])
            total += abs(orders[price])

        return expected_val, total
    
    def _append_buys(self, symbol: Symbol, own_trades: List[Trade]):
      for trade in own_trades:
          if trade.buyer != '':
              self.all_buys[symbol].append(trade.price)
          elif trade.seller != '':
              self.all_buys[symbol].remove(min(self.all_buys[symbol]))

    def do_order(self, bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
        reverse = False
        if trade_made == "SELL":
            reverse = True
        tradeHappened = False
        orders_sorted = sorted(bot_orders.keys(), reverse = reverse)

        all_prices = []
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
                    tradeHappened = True
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -vol_to_trade))
                    tradeHappened = True
                all_prices.append(prices)
            else: 
                break
            if max_vol <= 0:
                break
                    
        if not tradeHappened:
          self.marketmake(product=product, tradeMade=trade_made, quantity=10, acceptablePrice=acceptable_price, volume=max_vol, orderList=order_lst)
          return None

        else:
            return all_prices

          

    def get_expected_price(self, state: TradingState) -> Dict[str, float]:

      ret: Dict[str, float] = {}
      for product in state.order_depths.keys():              
        expected_val = 0
        total = 0

        buy_orders = state.order_depths[product].buy_orders
        sell_orders = state.order_depths[product].sell_orders

        max_buy = max(buy_orders.keys())
        min_ask = min(sell_orders.keys())
                
        ret[product] = ((min_ask + max_buy)/2, max_buy, min_ask)

      return ret
    

    def marketmake(self, product, tradeMade, quantity, acceptablePrice, volume, orderList):
        
        if tradeMade == "BUY":
            less = (volume+quantity-1)//quantity
            for i in range(int(acceptablePrice) - 2, int(acceptablePrice) - 2 - less, -1):
                vol = quantity if volume >= quantity else volume
                print("BUY", str(-vol) + "x", i)
                orderList.append(Order(product, i, vol))
                volume -= vol
        elif tradeMade == "SELL":
            less = (volume+quantity-1)//quantity
            for i in range(int(acceptablePrice) + 2, int(acceptablePrice) + 2 + less):
                vol = quantity if volume >= quantity else volume
                print("SELL", str(vol) + "x", i)
                orderList.append(Order(product, i, -vol))
                volume -= vol
        else:
            return None
      
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        expected_val_dict = self.get_expected_price(state)
        print(len(self.cache))


        day = state.timestamp
       

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            if product == "BANANAS":
                pos = state.position.get(product, 0)
                max_buy = 20 - pos
                max_sell= abs(-20 - pos)
                expected_val_tup = expected_val_dict[product]
                expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup

                self.cache.append(expected_val_total)

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                ## patel calls function gets model

                # model = self._best_fit_line(self.cache

                
                buy_prices = None
                sell_prices = None
                middle = -1
                if len(self.cache) >= Trader.window_size:
                  z_score = self.z_score(expected_val_total)
                  z_thresh = 1.5
                  middle = self.rolling_mean()

                  if z_score < -z_thresh :
                      buy_prices = self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle - 1, trade_made="BUY", product=product, order_lst = orders)
                  # self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle, trade_made="BUY", product=product, order_lst = orders)
                  elif z_score > z_thresh:
                      sell_prices = self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle + 1, trade_made="SELL", product=product, order_lst = orders)
                  else:
                    self.marketmake(product=product, tradeMade="BUY", quantity=10, acceptablePrice=middle, volume=max_buy, orderList=orders)
                    self.marketmake(product=product, tradeMade="SELL", quantity=10, acceptablePrice=middle, volume=max_sell, orderList=orders)
                  # else:
                  #      self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle - FACTOR, trade_made="BUY", product=product, order_lst = orders)
                  #      self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle + FACTOR, trade_made="SELL", product=product, order_lst = orders)



                  result[product] = orders

                  print_str = ['\nFOR_PLOT']

                  print_str.append('TIMESTAMP')
                  print_str.append(str(state.timestamp))

                  print_str.append('TRUE_MID')
                  print_str.append(str(expected_val_total))

                  print_str.append('MAX_BUY')
                  print_str.append(str(expected_val_buy))

                  print_str.append('MIN_ASK')
                  print_str.append(str(expected_val_sell))

                  print_str.append('PRED_MIDDLE')
                  print_str.append(str(middle))



                  print_str.append('BUY_PRICES')
                  print_str.append(str(buy_prices[0] if buy_prices != None else None))

                  print_str.append('SELL_PRICES')
                  print_str.append(str(sell_prices[0] if sell_prices != None else None))

                  print_str = ':'.join(print_str)
                  print(print_str)


                import itertools

                # print("Left of Cache: ", self.cache[0])
                # print("Right of Cache: ", self.cache[-1])
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

        self.current_iter += 100


                


        return result
    
def main():
    timestamp = 1000

    listings = {
        "BANANAS": Listing(
            symbol="BANANAS", 
            product="BANANAS", 
            denomination= "SEASHELLS"
        ),
        "PEARLS": Listing(
            symbol="PEARLS", 
            product="PEARLS", 
            denomination= "SEASHELLS"
        ),
    }

    od = OrderDepth()
    od.buy_orders = {10: 7, 9: 5}
    od.sell_orders = {11: -4, 12: -8}

    od2 = OrderDepth()
    od2.buy_orders = {142: 3, 141: 5}
    od2.sell_orders = {144: -5, 145: -8}

    order_depths = {
        "BANANAS": od,
        "PEARLS": od2,	
    }

    own_trades = {
        "BANANAS": [],
        "PEARLS": []
    }

    market_trades = {
        "BANANAS": [
            Trade(
                symbol="BANANAS",
                price=11,
                quantity=4,
                buyer="",
                seller="",
                timestamp=900
            )
        ],
        "PEARLS": []
    }

    position = {
        "BANANAS": 3,
        "PEARLS": -5
    }

    observations = {}

    state = TradingState(
        timestamp=timestamp,
        listings=listings,
        order_depths=order_depths,
        own_trades = own_trades,
        market_trades = market_trades,
        position = position,
        observations = observations
    )
    trader1 = Trader()
    trader1.run(state)

if __name__ == "__main__":
    main()