



from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Symbol, Trade
import operator
from collections import defaultdict
import pandas as pd
import numpy as np
class Trader:

    last_exp = {}
    last_slope = {}
    all_buys: Dict[Symbol, List[float]] = defaultdict(list)


    def _best_fit_line(self, pairs: pd.DataFrame = None):
        x = pairs['timestamp']
        y = pairs['price']

        assert len(pairs) == 10000

        return np.poly1d(np.polyfit(x, y, 3))


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
        print(buy_orders)
        print(sell_orders)
        
        exp_buy, total_buy = self._get_expected_total(state.order_depths[product].buy_orders)
        exp_sell, total_sell = self._get_expected_total(state.order_depths[product].sell_orders)

        expected_val = exp_buy + exp_sell
        total = total_buy  + total_sell

        expected_val_total = expected_val/total if total != 0 else (self.last_slope[product]if product in self.last_slope else 0)

        expected_val_buy = exp_buy/total_buy if total_buy != 0 else 0
        expected_val_sell = exp_sell/total_sell if total_sell != 0 else float('inf')
        
        ret[product] = (expected_val_total, expected_val_buy, expected_val_sell)

      return ret

    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        expected_val_dict = self.get_expected_price(state)
      

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            pos = state.position.get(product, 0)
            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]
            
            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []

            ## patel calls function gets model

            model = self._best_fit_line(cache)

            middle = model(state.timestamp)


        return result
