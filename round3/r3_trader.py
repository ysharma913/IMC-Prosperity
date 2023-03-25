from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Trade, Listing, Symbol
from collections import deque
import operator
import numpy as np
import math, statistics
import pandas as pd
# from PairsTrader import PairsTrader


class Trader:
    
    limits = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300}
    
    class PairsTrader:
      def __init__(self, product_a: str, product_b: str, z_thresh:float, window_size: int, historical_avg =0.5315710740336883):
        self.product_a: str = product_a
        self.product_b: str = product_b
        self.z_thresh: float = z_thresh

        self.rolling_ratio: list = [historical_avg] *  window_size
        self.historical_avg = historical_avg

        self.window_size = window_size

      def z_score(self, ratio: float) -> float:
        window_arr = np.array(self.rolling_ratio[-self.window_size-1:-1])
        return (ratio - window_arr.mean())/window_arr.std()

      # return the list of orders this algorithm is to make 
      def make_orders(self, state: TradingState) -> List[Order]:
        # get the current stock price and the spread
        stock_price_a, _, _ = Trader.get_spread(state, self.product_a)
        stock_price_b, _, _ = Trader.get_spread(state, self.product_b)

        # get the ratio between the 2 stocks and append to list
        ratio = stock_price_a / stock_price_b
        self.rolling_ratio.append(ratio)
        # print('Window Sizes', len(self.rolling_ratio))
        if len(self.rolling_ratio) < self.window_size - 1:
           return [], []
        product_a_order_depth: OrderDepth = state.order_depths[self.product_a]
        product_b_order_depth: OrderDepth = state.order_depths[self.product_b]

        product_a_orders: list[Order] = list()
        product_b_orders: list[Order] = list()
        

        z_score = self.z_score(ratio)

        # low z_score means that a/b is far less than average
        # a/b 
        # -> a is small and b is big
        # long a and short b
        buy_vol_a, sell_vol_a = Trader.get_max_min_vols(state, self.product_a)
        buy_vol_b, sell_vol_b = Trader.get_max_min_vols(state, self.product_b)
        if z_score < -self.z_thresh:
          # long a
          Trader.do_order(
            product= self.product_a,
            bot_orders= product_a_order_depth.sell_orders,
            max_vol= buy_vol_a,
            trade_made= "BUY",
            order_lst= product_a_orders,
          )

          # short b
          Trader.do_order(
            product= self.product_b,
            bot_orders= product_b_order_depth.buy_orders,
            max_vol= sell_vol_b,
            trade_made= "SELL",
            order_lst= product_b_orders
          )

        elif z_score > self.z_thresh:
          # short a
          Trader.do_order(
            product= self.product_a,
            bot_orders= product_a_order_depth.buy_orders,
            max_vol= sell_vol_a,
            trade_made= "SELL",
            order_lst= product_a_orders
          )

          # long b
          Trader.do_order(
            product= self.product_b,
            bot_orders= product_b_order_depth.sell_orders,
            max_vol= buy_vol_b,
            trade_made= "BUY",
            order_lst= product_b_orders
          )

        return product_a_orders, product_b_orders


    pairs_trader = PairsTrader(
        "COCONUTS", 
        'PINA_COLADAS', 
        z_thresh = 1.25, 
        window_size= 500
      )

    def get_max_min_vols(state, product):
        pos = state.position.get(product, 0)
        limit = Trader.limits[product]
        max_buy = limit - pos
        max_sell = abs(-limit - pos)
        return max_buy, max_sell

    def get_spread(state: TradingState, product: str) -> Dict[str, float]:

      ret: Dict[str, float] = {}
      expected_val = 0
      total = 0

      buy_orders = state.order_depths[product].buy_orders
      sell_orders = state.order_depths[product].sell_orders

      max_buy = max(buy_orders.keys())
      min_ask = min(sell_orders.keys())
              
      ret =  ((min_ask + max_buy)/2, max_buy, min_ask)

      return ret
    

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
    
    def do_order(bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
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

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        result:  Dict[str, List[Order]] = {}
        a_orders, b_orders = self.pairs_trader.make_orders(state)
        result[self.pairs_trader.product_a] = a_orders
        result[self.pairs_trader.product_b] = b_orders
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
