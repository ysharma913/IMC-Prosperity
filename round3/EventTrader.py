from r3_trader import PairsTrader, StaticTrader
import typing
from datamodel import OrderDepth, TradingState, Order, Trade, Listing, Symbol
from typing import Dict, List, Tuple

class EventTrader(PairsTrader):

    def __init__(self, product_a: str, product_b: str, z_thresh: float, window_size: int, historical_avg=0.5315710740336883):
        super().__init__(product_a, product_b, z_thresh, window_size, historical_avg)

    def make_orders(self, state: TradingState) -> List[Order]:
        stock_price_a, _, _ = StaticTrader.get_product_expected_price(self, self.product_a)

        observation_b = StaticTrader.get_observation(state, self.product_b)

        ratio = stock_price_a / observation_b

        self.rolling_ratio.append(ratio)

        if len(self.rolling_ratio) < self.window_size - 1:
           return [], []
        
        z_score = self.z_score(ratio)

        reversion_a_action: Dict[str, List[Order]] = self.mean_reversion_a.make_orders(state)[self.product_a]

        if (z_score < -self.z_thresh and 
            len(reversion_a_action) > 0 and
            reversion_a_action[0].quantity
            ):

            action_a = reversion_a_action
        elif (z_score > self.z_thresh and
            len(reversion_a_action) > 0 and
            reversion_a_action[0].quantity < 0
            ):
            action_a = reversion_a_action

        return {self.product_a: action_a}
