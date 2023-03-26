from r3_trader import Trader
from datamodel import OrderDepth, TradingState, Order, Trade, Listing, Symbol
import numpy as np
from typing import Dict, List, Tuple

class PairsTrader:
    def __init__(self, product_a: str, product_b: str, z_thresh:float, window_size: int, historical_avg =0.5315710740336883):
        self.product_a: str = product_a
        self.product_b: str = product_b
        self.z_thresh: float = z_thresh

        self.rolling_ratio: list = [historical_avg] *  window_size
        self.historical_avg = historical_avg

        self.window_size = window_size

        # a/b
        # if the z score is high
        # a/b is too big
        # -> a is too big and b to small
        # -> a is too big and b correct
        # -> a is fair and b is too small

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
            Trader.do_order_volume(
            product= self.product_a,
            bot_orders= product_a_order_depth.sell_orders,
            max_vol= buy_vol_a,
            trade_made= "BUY",
            order_lst= product_a_orders
            )

            # short b
            Trader.do_order_volume(
            product= self.product_b,
            bot_orders= product_b_order_depth.buy_orders,
            max_vol= sell_vol_b,
            trade_made= "SELL",
            order_lst= product_b_orders
            )

        elif z_score > self.z_thresh:
            # short a
            Trader.do_order_volume(
            product= self.product_a,
            bot_orders= product_a_order_depth.buy_orders,
            max_vol= sell_vol_a,
            trade_made= "SELL",
            order_lst= product_a_orders
            )

            # long b
            Trader.do_order_volume(
            product= self.product_b,
            bot_orders= product_b_order_depth.sell_orders,
            max_vol= buy_vol_b,
            trade_made= "BUY",
            order_lst= product_b_orders
            )

        return product_a_orders, product_b_orders