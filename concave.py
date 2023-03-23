from typing import Dict, List, Tuple
from datamodel import OrderDepth, TradingState, Order, Symbol, Trade, Listing
import operator
from collections import defaultdict

class Trader:

    last_exp = {}
    last_slope = {}
    limit_dict = {"BANANAS": 20, "PEARLS": 20, "COCONUTS": 600, "PINA_COLADAS": 300}

    def _best_fit_line(pairs: List[Tuple[float]]= None):
      if pairs is None:
        all_day_data = pd.DataFrame()
        last_timestamp = 0
        for i in range(3):
            day_i_data = pd.read_csv(f'island-data-bottle-round-1/trades_round_1_day_{i-2}_nn.csv', sep=';')
            day_i_data = day_i_data[day_i_data['symbol'] == "BANANAS"]
            day_i_data['timestamp'] += last_timestamp 
            all_day_data = pd.concat([all_day_data, day_i_data], axis=0)

            last_timestamp = day_i_data['timestamp'].iloc[-1] + 1

        all_day_data = all_day_data[all_day_data['price'] > 2000]

        

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
        if trade_made == "SELL":
            print("BUY ORDERS: ", str(bot_orders))
        else:
            print("SELL ORDERS: ", str(bot_orders))
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
        return (x < 0 and y > 0) or (x > 0 and y < 0)
     
    def flood(self, max_vol, acceptable_price, trade_made, product, order_lst):
        denomination = self.limit_dict[product]//2
        less = (max_vol+denomination - 1)//denomination
        if trade_made == "BUY":
            # how many sets of orders want to make
            # max_vol = 10, less = 2
            for i in range(int(acceptable_price) - 2, int(acceptable_price) - 2 - less, -1):
                vol = min(max_vol, denomination)
                print("FLOOD BUY", str(-vol) + "x", i)
                order_lst.append(Order(product, i, vol))
                max_vol -= vol

        elif trade_made == "SELL":
            for i in range(int(acceptable_price) + 2, int(acceptable_price) + 2 + less):
                vol = min(max_vol, denomination)
                print("FLOOD SELL", str(vol) + "x", i)
                order_lst.append(Order(product, i, -vol))
                max_vol -= vol

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        """
        Only method required. It takes all buy and sell orders for all symbols as an input,
        and outputs a list of orders to be sent
        """
        # Initialize the method output dict as an empty dict
        result = {}
        expected_val_dict = self.get_expected_price(state)
        try:
            print("PINA TRADE MADES: ", str(state.own_trades["PINA_COLADAS"]))
        except:
            pass

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():

            pos = state.position.get(product, 0)
            limit = self.limit_dict[product]
            max_buy = limit- pos
            max_sell= abs(-limit- pos)
            expected_val_tup = expected_val_dict[product]
            expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup
            # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
            order_depth: OrderDepth = state.order_depths[product]
            
            # if product in state.own_trades.keys():
            #   self._append_buys(product, state.own_trades[product])

            # Initialize the list of Orders to be sent as an empty list
            orders: list[Order] = []
            # print("**** ALL BUYS ****", self.all_buys)
         
            # if product in self.last_exp:
                
            #     last_exp = self.last_exp[product]
            #     slope = (expected_val_total - last_exp)/1
            #     last_slope = self.last_slope[product]

            #     if self.opposite_signs(slope, last_slope):
            #         print("expected_val",  expected_val_total)
            #         print("expected_val_buy", expected_val_buy)
            #         print("expected_val_sell", expected_val_sell)
            #         # slope changed from neg to pos, buy
            #         if slope > last_slope:

            #             # 
            #             min_ask = min(order_depth.sell_orders.keys()) * 1.05
            #             self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= min_ask, trade_made="BUY", product=product, order_lst = orders)

            #         elif slope < last_slope:
            #             min_buy = min(self.all_buys[product]) if len(self.all_buys[product]) > 0 else None
            #             if min_buy:
            #               self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= min_buy, trade_made="SELL", product=product, order_lst = orders)

            #     result[product] = orders
            #     self.last_slope[product] = slope
            # else:
            #     self.last_slope[product] = 0

            if product == 'COCONUTS':
                
                product_pina = "PINA_COLADAS"
                pos = state.position.get(product_pina, 0)
                limit = self.limit_dict[product_pina]
                max_buy_pina = limit- pos
                max_sell_pina= abs(-limit- pos)
                expected_val_pina_tup = expected_val_dict[product_pina]
                expected_val_total_pina, expected_val_buy_pina, expected_val_sell_pina = expected_val_pina_tup
            
                
                pina_orders: list[Order] = []
                pina_order_depth: OrderDepth = state.order_depths[product_pina]

                # need to figure out how many pina coladas to buy?

                # product has a last expected_value
                if product in self.last_exp:
                
                   
                    slope = expected_val_total - self.last_exp[product] 
                    last_slope = self.last_slope.get(product, slope)

                    print("slope: " + str(slope))
                    print("last_slope: " + str(last_slope))
                    print("CURRENT PINA ORDERS SELLS: ", str(pina_order_depth.sell_orders))
                    print("CURRENT PINA ORDERS BUYS: ", str(pina_order_depth.buy_orders))
                    # if self.opposite_signs(slope, last_slope):
                    # slope changed from ned to pos, buy
                    if slope > last_slope:

                        print("FLOODING COCONUTS UP, BUYING PINA")
                        # # flood coconuts and buy pinacoladas
                        # self.flood(max_vol = max_sell, acceptable_price= expected_val_total, trade_made="SELL", product=product, order_lst = orders)

                        self.do_order(bot_orders = pina_order_depth.sell_orders, operator = operator.lt, max_vol = max_buy_pina, acceptable_price= expected_val_sell_pina, trade_made="BUY", product=product_pina, order_lst = pina_orders)

                    elif slope < last_slope:
                        
                        print("FLOODING COCONUTS DOWN, SELLING PINA")
                        # self.flood(max_vol = max_buy, acceptable_price= expected_val_total, trade_made="BUY", product=product, order_lst = orders)

                        self.do_order(bot_orders = pina_order_depth.buy_orders, operator = operator.gt, max_vol = max_sell_pina, acceptable_price= expected_val_buy_pina, trade_made="SELL", product=product_pina, order_lst = pina_orders)
                    
                    print("actual pina trades: ", str(pina_orders))
                    self.last_slope[product] = slope
                    result[product_pina] = pina_orders
                    result[product] = orders
                else:
                    self.last_slope[product] = 0
            
            self.last_exp[product] = expected_val_total
       

        print("TRADE BOOK: ", str(result))
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

if __name__ == "__main__":
    main()