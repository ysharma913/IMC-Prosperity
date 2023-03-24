
from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Symbol, Trade, Listing
import operator
from collections import defaultdict, deque
import pandas as pd
import numpy as np
class Trader:

    current_iter = 0
    cache = deque(((-60000, 4811.5), (-59700, 4811.0), (-59400, 4812.0), (-59100, 4810.5), (-58800, 4814.5), (-58500, 4809.5), (-58200, 4815.5), (-57900, 4811.5), (-57600, 4816.5), (-57300, 4814.0), (-57000, 4816.0), (-56700, 4815.5), (-56400, 4815.5), (-56100, 4815.0), (-55800, 4815.0), (-55500, 4815.5), (-55200, 4816.0), (-54900, 4815.5), (-54600, 4815.5), (-54300, 4815.5), (-54000, 4816.5), (-53700, 4813.5), (-53400, 4817.5), (-53100, 4818.0), (-52800, 4816.0), (-52500, 4817.0), (-52200, 4816.5), (-51900, 4817.0), (-51600, 4818.5), (-51300, 4813.5), (-51000, 4817.0), (-50700, 4816.5), (-50400, 4818.0), (-50100, 4818.0), (-49800, 4819.0), (-49500, 4822.0), (-49200, 4819.0), (-48900, 4820.0), (-48600, 4817.5), (-48300, 4817.0), (-48000, 4818.5), (-47700, 4820.0), (-47400, 4818.0), (-47100, 4820.0), (-46800, 4819.5), (-46500, 4822.0), (-46200, 4819.0), (-45900, 4816.5), (-45600, 4819.5), (-45300, 4819.0), (-45000, 4820.5), (-44700, 4822.5), (-44400, 4818.0), (-44100, 4817.0), (-43800, 4818.5), (-43500, 4821.5), (-43200, 4822.0), (-42900, 4820.0), (-42600, 4820.5), (-42300, 4821.0), (-42000, 4822.0), (-41700, 4821.5), (-41400, 4822.0), (-41100, 4821.0), (-40800, 4822.0), (-40500, 4821.5), (-40200, 4824.5), (-39900, 4824.0), (-39600, 4822.5), (-39300, 4822.5), (-39000, 4820.5), (-38700, 4821.0), (-38400, 4822.0), (-38100, 4822.5), (-37800, 4822.5), (-37500, 4822.0), (-37200, 4820.0), (-36900, 4822.5), (-36600, 4822.0), (-36300, 4822.0), (-36000, 4822.0), (-35700, 4822.5), (-35400, 4823.0), (-35100, 4825.5), (-34800, 4822.5), (-34500, 4820.0), (-34200, 4821.5), (-33900, 4822.5), (-33600, 4823.0), (-33300, 4823.0), (-33000, 4821.0), (-32700, 4820.5), (-32400, 4821.0), (-32100, 4823.5), (-31800, 4823.0), (-31500, 4820.5), (-31200, 4822.0), (-30900, 4822.0), (-30600, 4821.0), (-30300, 4820.0), (-30000, 4820.5), (-29700, 4821.0), (-29400, 4821.5), (-29100, 4822.0), (-28800, 4822.5), (-28500, 4823.5), (-28200, 4820.5), (-27900, 4820.5), (-27600, 4822.5), (-27300, 4820.5), (-27000, 4820.5), (-26700, 4822.0), (-26400, 4821.0), (-26100, 4820.5), (-25800, 4821.5), (-25500, 4823.0), (-25200, 4822.0), (-24900, 4821.5), (-24600, 4821.5), (-24300, 4821.5), (-24000, 4823.0), (-23700, 4822.0), (-23400, 4822.0), (-23100, 4821.5), (-22800, 4822.0), (-22500, 4820.5), (-22200, 4821.5), (-21900, 4823.0), (-21600, 4820.0), (-21300, 4823.5), (-21000, 4822.0), (-20700, 4822.5), (-20400, 4820.5), (-20100, 4822.0), (-19800, 4822.5), (-19500, 4822.0), (-19200, 4823.5), (-18900, 4824.0), (-18600, 4823.5), (-18300, 4821.5), (-18000, 4824.0), (-17700, 4825.5), (-17400, 4825.0), (-17100, 4821.5), (-16800, 4826.5), (-16500, 4823.5), (-16200, 4823.0), (-15900, 4824.5), (-15600, 4825.0), (-15300, 4825.0), (-15000, 4824.5), (-14700, 4824.0), (-14400, 4822.5), (-14100, 4822.5), (-13800, 4821.5), (-13500, 4823.5), (-13200, 4825.0), (-12900, 4824.0), (-12600, 4822.5), (-12300, 4825.0), (-12000, 4824.0), (-11700, 4821.5), (-11400, 4824.5), (-11100, 4822.5), (-10800, 4822.0), (-10500, 4822.5), (-10200, 4823.0), (-9900, 4822.5), (-9600, 4821.0), (-9300, 4821.5), (-9000, 4819.5), (-8700, 4821.5), (-8400, 4823.0), (-8100, 4821.5), (-7800, 4824.5), (-7500, 4822.0), (-7200, 4822.5), (-6900, 4822.0), (-6600, 4823.0), (-6300, 4822.5), (-6000, 4822.0), (-5700, 4821.5), (-5400, 4821.5), (-5100, 4820.5), (-4800, 4820.5), (-4500, 4819.0), (-4200, 4819.0), (-3900, 4820.0), (-3600, 4820.0), (-3300, 4820.5), (-3000, 4821.5), (-2700, 4822.5), (-2400, 4825.5), (-2100, 4825.5), (-1800, 4823.5), (-1500, 4823.5), (-1200, 4822.5), (-900, 4823.0), (-600, 4826.5), (-300, 4820.5)))
    limit_dict = {"BANANAS": 20, "PEARLS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}
    MODULO = 1
    STEP_SIZE = 100

    def _best_fit_line(self, pairs: List[Tuple[float]]):

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
                tradeHappened = True
                if trade_made == "BUY":
                    order_lst.append(Order(product, prices, vol_to_trade))
                   
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -vol_to_trade))
            else: 
                break
            if max_vol <= 0:
                break
        
        if not tradeHappened:
            denomination = self.limit_dict[product]//2
            less = (max_vol+denomination - 1)//denomination
            if trade_made == "BUY":

                # how many sets of orders want to make
                # max_vol = 10, less = 2
                for i in range(int(acceptable_price) - 2, int(acceptable_price) - 2 - less, -1):
                    vol = min(max_vol, denomination)
                    print("FLOOD BUY", str(-vol) + "x", i)
                   # order_lst.append(Order(product, i, vol))
                    max_vol -= vol
            elif trade_made == "SELL":
                for i in range(int(acceptable_price) + 2, int(acceptable_price) + 2 + less):
                    vol = min(max_vol, denomination)
                    print("FLOOD SELL", str(vol) + "x", i)
                 #   order_lst.append(Order(product, i, -vol))
                    max_vol -= vol

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
      
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        expected_val_dict = self.get_expected_price(state)

        # day = state.timestamp
        # current = ((day - 1) * 1_000_000) + self.current_iter
       

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            if product == "BANANAS":
                print(len(self.cache))
                pos = state.position.get(product, 0)
                max_buy = 20 - pos
                max_sell= abs(-20 - pos)
                expected_val_tup = expected_val_dict[product]
                print_str = ['FOR_PLOT']
                expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup

                print_str.append('TIMESTAMP')
                print_str.append(str(state.timestamp))

                print_str.append('TRUE_MID')
                print_str.append(str(expected_val_total))

                print_str.append('MAX_BUY')
                print_str.append(str(expected_val_buy))

                print_str.append('MIN_ASK')
                print_str.append(str(expected_val_sell))

                


                if state.timestamp % self.MODULO * self.STEP_SIZE == 0:
                  self.cache.popleft()
                  self.cache.append((state.timestamp, expected_val_total))

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                

                ## patel calls function gets model

                model = self._best_fit_line(self.cache)
                
                middle = model(state.timestamp)

                print_str.append('PRED_MIDDLE')
                print_str.append(str(middle))

                print_str = ':'.join(print_str)

                print(print_str)

                self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle, trade_made="BUY", product=product, order_lst = orders)

                self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle, trade_made="SELL", product=product, order_lst = orders)

                result[product] = orders

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
    # main()
    import tester
    main()

    # t = Trader()

    # tester._test_best_fit_line(t._best_fit_line)