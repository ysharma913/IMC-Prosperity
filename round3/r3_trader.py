from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Trade, Listing, Symbol
from collections import deque
import operator
import numpy as np
import math, statistics
import pandas as pd
# from PairsTrader import PairsTrader
# all the static trader functions
class StaticTrader:

    limits = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300, 'BERRIES': 250, 'DIVING_GEAR': 50}

    def marketmake(product, tradeMade, quantity, acceptablePrice, volume, orderList):
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
    
    def get_observation(state: TradingState, product: str):
        return state.observations[product]

class MeanReversion:

        def __init__(self, window_size: int, z_thresh: int, product : str):
            self.rolling_window = list()
            self.WINDOW_SIZE = window_size
            self.Z_THRESH = z_thresh
            self.product = product
            self.limit = StaticTrader.limits[product]

        # 
        def rolling_mean(self):
            return np.array(self.rolling_window[-self.WINDOW_SIZE - 1:-1]).mean().item()
        
        
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
            if len(self.rolling_window) >= self.WINDOW_SIZE:
                z_score = self.z_score(expected_val_total)
                middle = self.rolling_mean()
                if z_score < -self.Z_THRESH:
                    buy_prices = StaticTrader.do_order_price(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle, trade_made="BUY", product=self.product, order_lst = orders, limit = self.limit)

                elif z_score > self.Z_THRESH:
                    sell_prices = StaticTrader.do_order_price(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle, trade_made="SELL", product=self.product, order_lst = orders, limit = self.limit)

                # else:
                #     StaticTrader.marketmake(product=self.product, tradeMade="BUY", quantity=10, acceptablePrice=middle, volume=max_buy, orderList=orders)

                #     StaticTrader.marketmake(product=self.product, tradeMade="SELL", quantity=10, acceptablePrice=middle, volume=max_sell, orderList=orders)

            return {self.product: orders}
    
class PairsTrader:
      def __init__(self, product_a: str, product_b: str, z_thresh:float, window_size: int, historical_avg =0.5315710740336883, mean_b = True):
        self.product_a: str = product_a
        self.product_b: str = product_b
        self.z_thresh: float = z_thresh

        self.rolling_ratio: list = [historical_avg] *  window_size
        self.historical_avg = historical_avg

        self.window_size = window_size
        self.mean_reversion_a = MeanReversion(
            window_size=300,
            z_thresh=1.5,
            product=product_a
        )
        if mean_b:
            self.mean_reversion_b = MeanReversion(
                window_size=400,
                z_thresh=1.5,
                product=product_b
            )

      def z_score(self, ratio: float) -> float:
        window_arr = np.array(self.rolling_ratio[-self.window_size-1:-1])
        return (ratio - window_arr.mean())/window_arr.std()

      # return the list of orders this algorithm is to make 
      def make_orders(self, state: TradingState) -> List[Order]:
        # get the current stock price and the spread
        stock_price_a, max_buy_a, min_ask_a = StaticTrader.get_product_expected_price(state, self.product_a)
        stock_price_b, max_buy_b, min_ask_b = StaticTrader.get_product_expected_price(state, self.product_b)

        # get the ratio between the 2 stocks and append to list
        ratio = stock_price_a / stock_price_b
        self.rolling_ratio.append(ratio)
        # print('Window Sizes', len(self.rolling_ratio))
        if len(self.rolling_ratio) < self.window_size - 1:
           {self.product_a: [], self.product_b:[]}
        product_a_order_depth: OrderDepth = state.order_depths[self.product_a]
        product_b_order_depth: OrderDepth = state.order_depths[self.product_b]

        product_a_orders: list[Order] = list()
        product_b_orders: list[Order] = list()
        

        z_score = self.z_score(ratio)


        reversion_a_action: Dict[str, List[Order]] = self.mean_reversion_a.make_orders(state)[self.product_a]
        reversion_b_action: Dict[str, List[Order]] = self.mean_reversion_b.make_orders(state)[self.product_b]
        action_a: List[Order] = []
        action_b: List[Order] = []
        if z_score < -self.z_thresh:
            # long a or do nothing with a
            if len(reversion_a_action) > 0 and reversion_a_action[0].quantity > 0:
                action_a = reversion_a_action
            # short b or do nothing with b
            if len(reversion_b_action) > 0 and reversion_b_action[0].quantity < 0:
                action_b = reversion_b_action
        
        elif z_score > self.z_thresh:
            # short a or do nothing with b
            if len(reversion_a_action) > 0 and reversion_a_action[0].quantity < 0:
                action_a = reversion_a_action
            # long b or do nothing with b
            if len(reversion_b_action) > 0 and reversion_b_action[0].quantity > 0:
                action_b = reversion_b_action

        return {
            self.product_a: action_a,
            self.product_b: action_b
        }

class EventTrader(PairsTrader):

    def __init__(self, product_a: str, product_b: str, z_thresh: float, window_size: int, historical_avg=0.5315710740336883):
        super().__init__(product_a, product_b, z_thresh, window_size, historical_avg, mean_b=False)

    def make_orders(self, state: TradingState) -> List[Order]:
        stock_price_a, _, _ = StaticTrader.get_product_expected_price(state, self.product_a)

        observation_b = StaticTrader.get_observation(state, self.product_b)

        ratio = stock_price_a / observation_b

        self.rolling_ratio.append(ratio)

        if len(self.rolling_ratio) < self.window_size - 1:
           return {self.product_a: []}
        
        z_score = self.z_score(ratio)

        reversion_a_action: Dict[str, List[Order]] = self.mean_reversion_a.make_orders(state)[self.product_a]
        action_a = []
        if (z_score < -self.z_thresh and 
            len(reversion_a_action) > 0 and
            reversion_a_action[0].quantity > 0
            ):
            action_a = reversion_a_action

        elif (z_score > self.z_thresh and
            len(reversion_a_action) > 0 and
            reversion_a_action[0].quantity < 0
            ):
            action_a = reversion_a_action

        return {self.product_a: action_a}

class Trader:

    wrappers = {
        "PEARLS": [],
        "BANANAS": [MeanReversion(window_size = 5, z_thresh = 1.5, product = "BANANAS")],
        "COCONUTS": [
            PairsTrader(
                product_a="COCONUTS",
                product_b="PINA_COLADAS",
                z_thresh=1.5,
                window_size=300
            )
        ],
        "PINA_COLADAS": [],
        "BERRIES": [],  
        "DIVING_GEAR": [
            EventTrader(
                product_a="DIVING_GEAR",
                product_b="DOLPHIN_SIGHTINGS",
                z_thresh=1.5,
                window_size=150
            )
        ]

    }
    def initData(self):
        self.initalizedStart = True
        self.regressions['PEARLS'] = []
        self.regressions['BANANAS'] = []

        self.regressions['COCONUTS'] = []
        self.regressions['PINA_COLADAS'] = []


    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        # result:  Dict[str, List[Order]] = {}
        # a_orders, b_orders = self.wrappers["COCONUTS"][0].make_orders(state)
        # result["COCONUTS"] = a_orders
        # result["PINA_COLADAS"] = b_orders
        # print(result)
        result = {}
        for product in state.order_depths:
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
