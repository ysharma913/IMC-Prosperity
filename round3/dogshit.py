from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Trade, Listing, Symbol
from collections import deque
import operator
import numpy as np
import math, statistics
import pandas as pd

# all the static trader functions
class StaticTrader:

    limits = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300, 'BERRIES': 250, 'DIVING_GEAR': 50}

    def marketmake(product, tradeMade, quantity, acceptablePrice, volume, orderList):
        quantity = int(quantity)
        volume = int(volume)
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
    
    def get_product_expected_price(state, product):
        buy_orders = state.order_depths[product].buy_orders
        sell_orders = state.order_depths[product].sell_orders

        max_buy = max(buy_orders.keys())
        min_ask = min(sell_orders.keys())
                
        return ((min_ask + max_buy)/2, max_buy, min_ask)

    def get_max_min_vols(state, product):
        pos = state.position.get(product, 0)
        limit = StaticTrader.limits[product]
        max_buy = limit - pos
        max_sell = abs(-limit - pos)
        return max_buy, max_sell
    
    def do_order_price(bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst, limit):
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
          StaticTrader.marketmake(product=product, tradeMade=trade_made, quantity=limit//2, acceptablePrice=acceptable_price, volume=max_vol, orderList=order_lst)
          return None

        else:
            return all_prices

    def do_order_volume(bot_orders, max_vol, trade_made, product, order_lst):
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

    def do_midpoint(sell_orders, buy_orders):
        return (min(sell_orders) + max(buy_orders)) / 2

class MeanReversion:

        def __init__(self, window_size: int, z_thresh: int, product : str):
            self.rolling_window = list()
            self.WINDOW_SIZE = window_size
            self.Z_THRESH = z_thresh
            self.product = product
            self.limit = StaticTrader.limits[product]

        # 
        def rolling_mean(self):
            return np.array(self.rolling_window[-self.WINDOW_SIZE - 1:-1]).mean()
        
        
        def z_score(self, x: float):
            last_window = np.array(self.rolling_window[-self.WINDOW_SIZE - 1: -1])

            return (x - last_window.mean())/last_window.std()


        # - return the list of orders, 
        def make_orders(self, state):
            
            print("MAKE ORDER")

            expected_val_tup = StaticTrader.get_product_expected_price(state, self.product)

            expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup
            self.rolling_window.append(expected_val_total)

            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[self.product]
            
            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            max_buy, max_sell = StaticTrader.get_max_min_vols(state, self.product)

            buy_prices = None
            sell_prices = None
            middle = -1
            print("ABOUT TO DO  MATH??")
            print("length of rolling window: ", str(len(self.rolling_window)))
            print("self window size: ", self.WINDOW_SIZE)

            if len(self.rolling_window) >= self.WINDOW_SIZE:
                z_score = self.z_score(expected_val_total)
                middle = self.rolling_mean()
                print("z_score: ", z_score)

                print("z_thresh: ", self.Z_THRESH)
                print("middle: ", middle)
                if z_score < -self.Z_THRESH:
                    buy_prices = StaticTrader.do_order_price(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle - 1, trade_made="BUY", product=self.product, order_lst = orders, limit = self.limit)

                elif z_score > self.Z_THRESH:
                    sell_prices = StaticTrader.do_order_price(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle + 1, trade_made="SELL", product=self.product, order_lst = orders, limit = self.limit)

                else:
                    StaticTrader.marketmake(product=self.product, tradeMade="BUY", quantity=10, acceptablePrice=middle, volume=max_buy, orderList=orders)

                    StaticTrader.marketmake(product=self.product, tradeMade="SELL", quantity=10, acceptablePrice=middle, volume=max_sell, orderList=orders)

            return {self.product: orders}

class SigSlope:
    
    def __init__(self, product, trend_name, window_size, threshold, end_phase_window_size):
        self.product = product
        self.trend_name = trend_name
        self.WINDOW_SIZE = window_size
        self.END_PHASE_WINDOW_SIZE = end_phase_window_size
        self.threshold = threshold
        self.flag = 0
        self.product_values = []
        self.sighting_values = []
        self.limit = StaticTrader.limits[product]
    
    def is_steep(self, state):
        current_slope = (self.sighting_values[-1] - self.sighting_values[-1 - self.WINDOW_SIZE])
        
        if current_slope < -self.threshold:
            return -1
        elif current_slope > self.threshold:
            return 1
        
        return 0

    def make_orders(self, state):
        orders: list[Order] = []
        order_depth: OrderDepth = state.order_depths[self.product]

        max_buy_vol, max_sell_vol = StaticTrader.get_max_min_vols(state, self.product)
        current_price, _, _ = StaticTrader.get_product_expected_price(state, self.product)

        # self.product_values.append(current_price)
        self.sighting_values.append(state.observations[self.trend_name])

        gap = max(self.END_PHASE_WINDOW_SIZE, self.WINDOW_SIZE)
        if state.timestamp > gap * 100:
            prod_slopes = []
            for i in range(self.END_PHASE_WINDOW_SIZE):
                prod_slopes.append(self.sighting_values[-1 - i] - self.sighting_values[-2 - i])
                # prod_slopes.append(self.product_values[-1 - i] - self.product_values[-2 - i])
            prod_slopes = np.array(prod_slopes)

            if self.flag == 1 and prod_slopes.mean() <= 0:
                StaticTrader.do_order_volume(order_depth.buy_orders, max_sell_vol, 'SELL', self.product, orders)
                self.flag = 0
                print('Ended Positive Threshold Phase')
            elif self.flag == -1 and prod_slopes.mean() >= 0:
                StaticTrader.do_order_volume(order_depth.sell_orders, max_buy_vol, 'BUY', self.product, orders)
                self.flag = 0
                print('Ended Negative Threshold Phase')
            else:
                signal = self.is_steep(state)
                if signal == -1:
                    StaticTrader.do_order_volume(order_depth.buy_orders, max_sell_vol, 'SELL', self.product, orders)
                    self.flag = -1
                    print('Negative Threshold met')
                elif signal == 1:
                    StaticTrader.do_order_volume(order_depth.sell_orders, max_buy_vol, 'BUY', self.product, orders)
                    self.flag = 1
                    print('Positive Threshold met')

        return {self.product: orders}

    

class Trader:

    wrappers = {
        "PEARLS": [],
        "BANANAS": [],
        "COCONUTS": [],
        "PINA_COLADAS": [],
        "BERRIES": [],
        "DIVING_GEAR": [SigSlope(product = 'DIVING_GEAR',trend_name = 'DOLPHIN_SIGHTINGS', window_size = 1, threshold = 5, end_phase_window_size = 10)],
        "DOLPHIN_SIGHTINGS": [],
        "PICNIC_BASKET": [],
        "BAGUETTE": [],
        "UKULELE": [],
        "DIP": []
    }
    # past_averages

    initalizedStart = False
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

    

    def getProductValue(self, product, currPrice):
        self.regressions[product] = self.regressions[product][1:] + [currPrice]
        model = np.poly1d(np.polyfit(np.arange(1, len(self.regressions[product])+1), np.array(self.regressions[product]), 1))
        return model(len(self.regressions[product]))
    
    
    def get_expected_price(self, state: TradingState) -> Dict[str, float]:

        ret: Dict[str, float] = {}
        for product in state.order_depths.keys():              

            buy_orders = state.order_depths[product].buy_orders
            sell_orders = state.order_depths[product].sell_orders

            max_buy = max(buy_orders.keys())
            min_ask = min(sell_orders.keys())
                    
            ret[product] = ((min_ask + max_buy)/2, max_buy, min_ask)

        return ret    
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        # 500, z_thresh = 1.25
        WINDOW_SIZE = 500
        if not self.initalizedStart:
            self.initData()
        
        # expected_val_dict = self.get_expected_price(state)
        # print(len(self.cache)
        
        result = {}
        for product in state.order_depths.keys():
            precedent_lst = self.wrappers[product]
            for algo in precedent_lst:
                order_dict = algo.make_orders(state)
                for prod in order_dict:
                    order_lst = order_dict[prod]
                    if len(order_dict[prod]) > 0:
                        result[prod] = order_lst
                        break
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
        "DIVING_GEAR": Listing(
            symbol="DIVING_GEAR", 
            product="DIVING_GEAR", 
            denomination= "SEASHELLS"
        )
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

    od5 = OrderDepth()
    od5.buy_orders = {142: 3, 141: 5}
    od5.sell_orders = {144: -5, 145: -8}

    order_depths = {
        "BANANAS": od,
        "PEARLS": od2,	
        "COCONUTS": od3,
        "PINA_COLADAS": od4,
        "DIVING_GEAR": od5
    }

    own_trades = {
        "BANANAS": [],
        "PEARLS": [],
        "COCONUTS": [],
        "PINA_COLADAS": [],
        "DIVING_GEAR": []
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
        "PINA_COLADAS": -5,
        "DIVING_GEAR": 3
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
