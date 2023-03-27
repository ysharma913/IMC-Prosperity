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

    stop_losses = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300, 'BERRIES': 250, 'DIVING_GEAR': 50}

    order_book = {'PEARLS': {'BUY': [], 'SELL': []}, 'BANANAS': {'BUY': [], 'SELL': []}, 'COCONUTS': {'BUY': [], 'SELL': []}, 'PINA_COLADAS': {'BUY': [], 'SELL': []}, 'BERRIES': {'BUY': [], 'SELL': []}, 'DIVING_GEAR': {'BUY': [], 'SELL': []}}

    def stop_loss(state, product):  

        # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
        order_depth: OrderDepth = state.order_depths[product]
        
        # Initialize the list of Orders to be sent as an empty list
        orders: list[Order] = []

        mid_price = StaticTrader.do_midpoint(order_depth.sell_orders, order_depth.buy_orders)

        for trade in StaticTrader.order_book[product]:
            # reverse False - low to high

            # buys - high, if its that much higher than price, sell out

            # lows - low, if its that much lower than price, buy back


            reverse = True
            compare_op = operator.lt
            limit = StaticTrader.stop_losses[product]
            range_operator = operator.sub
            if trade == "SELL":
                reverse = False
                compare_op = operator.gt
                range_operator = operator.add
            
            our_orders = StaticTrader.order_book[product][trade]

           
            for i in range(len(our_orders)):
                price = our_orders[i](0)
                volume = our_orders[i](1):
                acceptable_loss = range_operator(price, limit)

                # if surpassed stop loss
                if compare_op(price, acceptable_loss):
                    
                    StaticTrader.put_order(product, price, volume * -1, orders, i)


                




        pass


    def put_order(product, price, vol, order_lst):
        trade_made = 'SELL'
        if vol > 0:
            trade_made = 'BUY'

        # tuples are organized: (price, volume)
        trade_to_search = 'SELL' if trade_made == 'BUY' else 'BUY'
        for price, volume in StaticTrader.order_book[product][trade_to_search]:
            volume_to_trade = min(volume, vol)



        StaticTrader.order_book[product][trade_made].append((price, vol))   
        order_lst.append(Order(product, price, vol))

    def marketmake(product, tradeMade, acceptablePrice, volume, orderList):
        quantity = int((StaticTrader.limits[product] // math.sqrt(StaticTrader.limits[product])) * 2)
        if tradeMade == "BUY":
            less = int((volume+quantity-1)//quantity)
            for i in range(int(acceptablePrice) - 2, int(acceptablePrice) - 2 - less, -1):
                vol = quantity if volume >= quantity else volume
                print("BUY", str(-vol) + "x", i)
                StaticTrader.put_order(product, i, vol, orderList)
                #orderList.append(Order(product, i, vol))
                volume -= vol
        elif tradeMade == "SELL":
            less = int((volume+quantity-1)//quantity)
            for i in range(int(acceptablePrice) + 2, int(acceptablePrice) + 2 + less):
                vol = quantity if volume >= quantity else volume
                print("SELL", str(vol) + "x", i)
                StaticTrader.put_order(product, -i, vol, orderList)
                # orderList.append(Order(product, i, -vol))
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
                    StaticTrader.put_order(product, prices, vol_to_trade, order_lst)
                    #order_lst.append(Order(product, prices, vol_to_trade))
                    tradeHappened = True
                elif trade_made == "SELL":
                    StaticTrader.put_order(product, prices, -vol_to_trade, order_lst)
                    #order_lst.append(Order(product, prices, -vol_to_trade))
                    tradeHappened = True
                all_prices.append(prices)
            else: 
                break
            if max_vol <= 0:
                break
                    
        if not tradeHappened:
          StaticTrader.marketmake(product=product, tradeMade=trade_made, acceptablePrice=acceptable_price, volume=max_vol, orderList=order_lst)
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
            # print("VOLUME TO TRADE: ", vol_to_trade)
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
                StaticTrader.put_order(product, prices, vol_to_trade, order_lst)
                #order_lst.append(Order(product, prices, vol_to_trade))

            elif trade_made == "SELL":
                StaticTrader.put_order(product, prices, -vol_to_trade, order_lst)
                #order_lst.append(Order(product, prices, -vol_to_trade))

            if max_vol <= 0:
                break
        return tradeHappened

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
                    buy_prices = StaticTrader.do_order_price(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle - 1, trade_made="BUY", product=self.product, order_lst = orders, limit = self.limit)

                elif z_score > self.Z_THRESH:
                    sell_prices = StaticTrader.do_order_price(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle + 1, trade_made="SELL", product=self.product, order_lst = orders, limit = self.limit)

                else:
                    StaticTrader.marketmake(product=self.product, tradeMade="BUY", acceptablePrice=middle, volume=max_buy, orderList=orders)

                    StaticTrader.marketmake(product=self.product, tradeMade="SELL", acceptablePrice=middle, volume=max_sell, orderList=orders)

            return {self.product: orders}

class BerriesMeanReversion:

        def __init__(self, big_window_size: int, small_window_size: int, z_thresh: int):
            self.rolling_window = list()
            self.BIG_WINDOW_SIZE = big_window_size
            self.SMALL_WINDOW_SIZE = small_window_size
            self.Z_THRESH = z_thresh
            self.product = "BERRIES"
            self.limit = StaticTrader.limits[self.product]
            self.consolidate = False
            self.mean_reversing = False
 
        def rolling_mean(self, window_size: int):
            return np.array(self.rolling_window[-window_size - 1:-1]).mean()
        
        
        def z_score(self, x: float, window_size: int):
            last_window = np.array(self.rolling_window[-window_size - 1: -1])

            return (x - last_window.mean())/last_window.std()

        def mean_reverse_volume(self, expected_val_total, order_depth, buy_volume, sell_volume, orders):
            z_score = self.z_score(expected_val_total, self.SMALL_WINDOW_SIZE)

            if z_score < -(self.Z_THRESH + .25):
               return StaticTrader.do_order_volume(bot_orders = order_depth.sell_orders, max_vol = buy_volume * 0.05, trade_made = "BUY", product = self.product, order_lst = orders)   

            elif z_score > (self.Z_THRESH + .25):
                return StaticTrader.do_order_volume(bot_orders = order_depth.buy_orders, max_vol = sell_volume * 0.05, trade_made = "SELL", product = self.product, order_lst = orders)

            return False
        
        # - return the list of orders, 
        def make_orders(self, state, iter):
            

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

            pos = state.position.get(self.product, 0)
            if len(self.rolling_window) >= self.BIG_WINDOW_SIZE:
                z_score = self.z_score(expected_val_total, self.BIG_WINDOW_SIZE)
                middle = self.rolling_mean(self.BIG_WINDOW_SIZE)

                trade_happened = False
                # quarter 2 = if middle is above mean # ALWAYS TRY TO BUY
                if iter in range(380_000, 500_000):
                   
                    if not self.mean_reversing:
                        trade_happened = StaticTrader.do_order_volume(bot_orders = order_depth.sell_orders, max_vol = max_buy, trade_made = "BUY", product = self.product, order_lst = orders)

                    # if not trade_happened:
                    #     self.mean_reversing = self.mean_reverse_volume(expected_val_total = expected_val_total, order_depth = order_depth, buy_volume = max_buy, sell_volume = max_sell, orders = orders)

                elif iter in range(500_000, 608_100):

                    if not self.mean_reversing:
                        trade_happened = StaticTrader.do_order_volume(bot_orders = order_depth.buy_orders, max_vol = max_sell, trade_made = "SELL", product = self.product, order_lst = orders)
                    
                    # if not trade_happened:
                    #     self.mean_reversing = self.mean_reverse_volume(expected_val_total = expected_val_total, order_depth = order_depth, buy_volume = max_buy, sell_volume = max_sell, orders = orders)
                    
                    if iter == 608_000:
                        self.rolling_window = list()
             
        
                else:
                    if z_score < -self.Z_THRESH:
                        buy_prices = StaticTrader.do_order_price(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle - 1, trade_made="BUY", product=self.product, order_lst = orders, limit = self.limit)

                    elif z_score > self.Z_THRESH:
                        sell_prices = StaticTrader.do_order_price(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle + 1, trade_made="SELL", product=self.product, order_lst = orders, limit = self.limit)

                    else:
                        StaticTrader.marketmake(product=self.product, tradeMade="BUY",acceptablePrice=middle, volume=max_buy, orderList=orders)

                        StaticTrader.marketmake(product=self.product, tradeMade="SELL",acceptablePrice=middle, volume=max_sell, orderList=orders)

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
            z_thresh=1.25,
            product=product_a
        )
        if mean_b:
            self.mean_reversion_b = MeanReversion(
                # 300 gave us cocos 13k, 1k, 
                window_size=400,
                z_thresh=1.25,
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
    # MeanReversion(window_size = 5, z_thresh = 1.5, product = "BANANAS")
    #BerriesMeanReversion(big_window_size = 5, small_window_size = 5, z_thresh = 1.25)
    wrappers = {
        "PEARLS": [],
        "BANANAS": [],
        "COCONUTS": [PairsTrader(
                product_a="COCONUTS",
                product_b="PINA_COLADAS",
                z_thresh=1.5,
                window_size=300
            )],
        "PINA_COLADAS": [],
        "BERRIES": [BerriesMeanReversion(big_window_size = 5, small_window_size = 5, z_thresh = 1.25)],
        "DIVING_GEAR": []

    }
    
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
        
        result = {}

        for product in state.order_depths.keys():

            if product not in self.wrappers:
                continue

            precedent_lst = self.wrappers[product]
            for algo in precedent_lst:
                if type(algo) == BerriesMeanReversion:
                    order_dict = algo.make_orders(state, state.timestamp)
                else:
                    order_dict = algo.make_orders(state)
                for prod in order_dict:
                    order_lst = order_dict[prod]
                    if len(order_dict[prod]) > 0:
                        result[prod] = order_lst
                        break
                if prod in result:
                    break
            
            # if didnt add a new trade, do stop_loss
            if product not in result:
                StaticTrader.stop_loss(state, product)

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
        "BERRIES": Listing(
            symbol="BERRIES", 
            product="BERRIES", 
            denomination= "SEASHELLS"
        ),
        "DIVING_GEAR": Listing(
            symbol="DIVING_GEAR", 
            product="DIVING_GEAR", 
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

    od5 = OrderDepth()
    od5.buy_orders = {142: 3, 141: 5}
    od5.sell_orders = {144: -5, 145: -8}


    od6 = OrderDepth()
    od6.buy_orders = {142: 3, 141: 5}
    od6.sell_orders = {144: -5, 145: -8}

    order_depths = {
        "BANANAS": od,
        "PEARLS": od2,	
        "COCONUTS": od3,
        "PINA_COLADAS": od4,	
        "BERRIES": od3,
        "DIVING_GEAR": od4,	
    }

    own_trades = {
        "BANANAS": [],
        "PEARLS": [],
        "COCONUTS": [],
        "PINA_COLADAS": [],
        "BERRIES": [],
        "DIVING_GEAR": [],	

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

