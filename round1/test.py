from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Symbol, Trade, Listing
import operator

class Trader:

    last_exp = {}
    last_slope = {}

    def _get_expected_total(self, orders: Dict[int, int]) -> Tuple[int]:
        expected_val = 0
        total = 0

        for price in orders.keys():
            expected_val += price * abs(orders[price])
            total += abs(orders[price])

        return expected_val, total


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
    
    def do_order(self, bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
        reverse = False
        if trade_made == "SELL":
            reverse = True
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
                if trade_made == "BUY":
                    order_lst.append(Order(product, prices, vol_to_trade))
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -vol_to_trade))
            else: 
                break
            if max_vol <= 0:
                break

    
    def opposite_signs(self, x, y):
        return (x < 0) if (y >= 0) else (y < 0)
    

    def do_order_match(self, bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
        reverse = False
        if trade_made == "SELL":
            reverse = True
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
                if trade_made == "BUY":
                    order_lst.append(Order(product, prices, vol_to_trade))
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -vol_to_trade))
            else: 
                break
            if max_vol <= 0:
                break
        return max_vol
    

    def do_flood(self, product, volume, price, order_lst):
        if volume < 0:
            print("SELL", str(volume) + "x", price)
        elif volume > 0:
            print("BUY", str(volume) + "x", price)
        if volume != 0:
            order_lst.append(Order(product, price, volume))
    
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
            max_buy = 20 - pos
            max_sell = abs(-20 - pos)
            expected_val_tup = expected_val_dict[product]
            expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup
            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []
         
            if product in self.last_exp:
                
                last_exp = self.last_exp[product]
                slope = (expected_val_total - last_exp)/1
                last_slope = self.last_slope[product]


                # why check slopes, just check if last_exp < this_exp, its going down so sell, if > then going up so buy
                if self.opposite_signs(slope, last_slope):
                    # slope changed from neg to pos, buy
                    max_ask =  max(order_depth.sell_orders.keys())
                    min_buy = min(order_depth.buy_orders.keys())
                    if slope > last_slope:
                        vol = self.do_order_match(
                                      bot_orders = order_depth.sell_orders, 
                                      operator = operator.lt, 
                                      max_vol = max_buy, 
                                      acceptable_price= expected_val_total, 
                                      trade_made="BUY", 
                                      product=product, 
                                      order_lst = orders)
                        
                        print("Mask Ask: ", max_ask)
                        print("Expected Total", expected_val_total)
                        self.do_flood(
                            product=product,
                            volume = -(max_sell - vol),
                            price = max_ask,
                            order_lst=orders
                        )

                    elif slope < last_slope:
                        vol = self.do_order_match(
                            bot_orders = order_depth.buy_orders, 
                            operator = operator.gt, 
                            max_vol = max_sell, 
                            acceptable_price= expected_val_total, 
                            trade_made="SELL", 
                            product=product, 
                            order_lst = orders)
                        
                        self.do_flood(
                            product=product,
                            volume = max_buy - vol,
                            price = min_buy,
                            order_lst= orders
                        )
                
                # thing going down, force it more down
                # elif slope < 0:


                self.last_slope[product] = slope


            else:
                self.last_slope[product] = 0

            result[product] = orders
            self.last_exp[product] = expected_val_total
            # if product == 'PEARLS':
            #     # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            #     order_depth: OrderDepth = state.order_depths[product]

            #     # Initialize the list of Orders to be sent as an empty list
            #     orders: list[Order] = []
    
            #     expected_val = expected_val_dict.get(product, slope)
            #     slope = expected_val - self.last_exp 
            #     last_slope = self.last_slope.get(product, slope)

            #     if self.opposite_signs(slope, last_slope):
            #         # slope changed from ned to pos, buy
            #         if slope > last_slope:
            #             self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= expected_val, trade_made="BUY", product=product, order_lst = orders)

            #         elif slope < last_slope:
            #             self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= expected_val, trade_made="SELL", product=product, order_lst = orders)
                
            #     result[product] = orders

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