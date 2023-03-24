from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Trade, Listing, Symbol
from collections import deque
import operator
import numpy as np
import math, statistics
import pandas as pd


class Trader:

    cache = list()

    # past_averages


    window_size = 5
    z_window_size = 5

    initalizedStart = False
    limits = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300}
    regressions = {}
    last_ticker = 0

    def initData(self):
        self.initalizedStart = True
        self.regressions['PEARLS'] = []
        self.regressions['BANANAS'] = []

        self.regressions['COCONUTS'] = []
        self.regressions['PINA_COLADAS'] = []
    
    def calculate_spread(self):
        coconuts = np.array(self.regressions['COCONUTS'])
        coladas = np.array(self.regressions['PINA_COLADAS'])

        ratio = pd.Series(coladas/coconuts)

        ratios_mavg5 = ratio.rolling(window=5, center=False).mean()
        ratios_mavg20 = ratio.rolling(window=20, center=False).mean()
        std_20 = ratio.rolling(window=20, center=False).std()
        zscore_20_5 = (ratios_mavg5 - ratios_mavg20)/std_20

        return zscore_20_5.iloc[-1]
    
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

    def getProductValue(self, product, currPrice):
        self.regressions[product] = self.regressions[product][1:] + [currPrice]
        model = np.poly1d(np.polyfit(np.arange(1, len(self.regressions[product])+1), np.array(self.regressions[product]), 1))
        return model(len(self.regressions[product]))
    
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
          self.marketmake(product=product, tradeMade=trade_made, quantity=self.limits[product]//2, acceptablePrice=acceptable_price, volume=max_vol, orderList=order_lst)
          return None

        else:
            return all_prices

    def do_order_volume(self, bot_orders, max_vol, trade_made, product, order_lst):
        reverse = False
        if trade_made == "SELL":
            reverse = True
        tradeHappened = False
        orders_sorted = sorted(bot_orders.keys(), reverse = reverse)
        for prices in orders_sorted:
            # if operator(prices, acceptable_price):
            volume = abs(bot_orders[prices])
            vol_to_trade = min(volume, max_vol)
            if vol_to_trade <= 0:
                break
            max_vol -= vol_to_trade
            # In case the lowest ask is lower than our fair value,
            # This presents an opportunity for us to buy cheaply
            # The code below therefore sends a BUY order at the price level of the ask,
            # with the same quantity
            # We expect this order to trade with the sell order
            tradeHappened = True
            print(trade_made, str(vol_to_trade) + "x", prices)
            if trade_made == "BUY":
                order_lst.append(Order(product, prices, vol_to_trade))

            elif trade_made == "SELL":
                order_lst.append(Order(product, prices, -vol_to_trade))

            if max_vol <= 0:
                break

    def do_midpoint(self, sell_orders, buy_orders):
        return (min(sell_orders) + max(buy_orders)) / 2
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        # 500, z_thresh = 1.25
        WINDOW_SIZE = 500
        if not self.initalizedStart:
            self.initData()
        
        expected_val_dict = self.get_expected_price(state)
        print(len(self.cache))
        day = state.timestamp
        
        result = {}
        for product in state.order_depths.keys():
            pos = state.position.get(product, 0)
            limit = self.limits[product]
            max_buy = limit - pos
            max_sell = abs(-limit - pos)
            order_depth: OrderDepth = state.order_depths[product]
            orders: list[Order] = []

            if product == 'PEARLS':
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
            if product == "BANANAS":
                expected_val_tup = expected_val_dict[product]
                expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup

                self.cache.append(expected_val_total)

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                
                buy_prices = None
                sell_prices = None
                middle = -1
                if len(self.cache) >= Trader.window_size:
                  z_score = self.z_score(expected_val_total)
                  z_thresh = 1.5
                  middle = self.rolling_mean()

                  if z_score < -z_thresh :
                      buy_prices = self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle - 1, trade_made="BUY", product=product, order_lst = orders)
                  elif z_score > z_thresh:
                      sell_prices = self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle + 1, trade_made="SELL", product=product, order_lst = orders)
                  else:
                    self.marketmake(product=product, tradeMade="BUY", quantity=10, acceptablePrice=middle, volume=max_buy, orderList=orders)
                    self.marketmake(product=product, tradeMade="SELL", quantity=10, acceptablePrice=middle, volume=max_sell, orderList=orders)



                result[product] = orders


            if product == "COCONUTS":

                product_pina = "PINA_COLADAS"
                pina_pos = state.position.get(product_pina, 0)
                pina_limit = self.limits[product_pina]
                max_buy_pina = pina_limit- pina_pos
                max_sell_pina= abs(-pina_limit- pina_pos)
                

                pina_orders: list[Order] = []
                pina_order_depth: OrderDepth = state.order_depths[product_pina]


                # append to regressions:
                coconut_midpoint = self.do_midpoint(order_depth.sell_orders, order_depth.buy_orders)
                colada_midpoint =  self.do_midpoint(pina_order_depth.sell_orders, pina_order_depth.buy_orders)
                self.regressions[product].append(coconut_midpoint)
                self.regressions[product_pina].append(colada_midpoint)

                z_score = self.calculate_spread()

                # print("Timestamp", state.timestamp)

                if state.timestamp/100 >= WINDOW_SIZE:
              
                    # need to figure out how many pina coladas to buy?
                    print("z-score", z_score)

                    z_thresh = 1.25
                    if z_score > z_thresh:
                        self.last_ticker = z_score
                        print("BUYING BOTH")
                        self.do_order_volume(bot_orders = pina_order_depth.sell_orders, max_vol = max_buy_pina, trade_made="BUY", product=product_pina, order_lst = pina_orders)

                        self.do_order_volume(bot_orders = order_depth.sell_orders, max_vol = max_buy, trade_made="BUY", product=product, order_lst = orders)

                    elif z_score < -z_thresh:
                        self.last_ticker = z_score
                        print("SELLING BOTH")
                        self.do_order_volume(bot_orders = pina_order_depth.buy_orders, max_vol = max_sell_pina, trade_made="SELL", product=product_pina, order_lst = pina_orders)

                        self.do_order_volume(bot_orders = order_depth.buy_orders, max_vol = max_sell, trade_made="SELL", product=product, order_lst = orders)

                    elif z_score > 1 and self.last_ticker > 0:
                        self.do_order_volume(bot_orders = pina_order_depth.sell_orders, max_vol = max_buy_pina, trade_made="BUY", product=product_pina, order_lst = pina_orders)

                        self.do_order_volume(bot_orders = order_depth.sell_orders, max_vol = max_buy, trade_made="BUY", product=product, order_lst = orders)
                    
                    elif z_score < -1 and self.last_ticker < 0:
                        self.do_order_volume(bot_orders = pina_order_depth.buy_orders, max_vol = max_sell_pina, trade_made="SELL", product=product_pina, order_lst = pina_orders)

                        self.do_order_volume(bot_orders = order_depth.buy_orders, max_vol = max_sell, trade_made="SELL", product=product, order_lst = orders)

                result[product] = orders
                result[product_pina] = pina_orders

        print(result)
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
        "COCONUTS": Listing(
            symbol="COCONUTS", 
            product="COCONUTS", 
            denomination= "SEASHELLS"
        ),
        "PINA_COLADAS": Listing(
            symbol="PINA_COLADAS", 
            product="PINA_COLADAS", 
            denomination= "SEASHELLS"
        ),
    }

    od = OrderDepth()
    od.buy_orders = {10: 7, 9: 5}
    od.sell_orders = {11: -4, 12: -8}

    od2 = OrderDepth()
    od2.buy_orders = {142: 3, 141: 5}
    od2.sell_orders = {144: -5, 145: -8}

    od3 = OrderDepth()
    od3.buy_orders = {142: 3, 141: 5}
    od3.sell_orders = {144: -5, 145: -8}

    od4 = OrderDepth()
    od4.buy_orders = {142: 3, 141: 5}
    od4.sell_orders = {144: -5, 145: -8}

    order_depths = {
        "BANANAS": od,
        "PEARLS": od2,	
        "COCONUTS": od3,
        "PINA_COLADAS": od4,	
    }

    own_trades = {
        "BANANAS": [],
        "PEARLS": [],
        "COCONUTS": [],
        "PINA_COLADAS": []
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
        "PEARLS": -5,
        "COCONUTS": 3,
        "PINA_COLADAS": -5
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

    # trader1.plotSpread()

if __name__ == "__main__":
    main()
