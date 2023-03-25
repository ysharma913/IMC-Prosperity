class Trader:

    def _best_fit_line(self, pairs: pd.DataFrame = None):

        x,y = zip(*pairs)
        x,y = np.array(x), np.array(y)

        assert len(pairs) == 2763
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
                if trade_made == "BUY":
                    order_lst.append(Order(product, prices, vol_to_trade))
                    tradeHappened = True
                elif trade_made == "SELL":
                    order_lst.append(Order(product, prices, -vol_to_trade))
                    tradeHappened = True
            else: 
                break
            if max_vol <= 0:
                break
        
        if not tradeHappened:
            if trade_made == "BUY":
                less = (max_vol+5)//6
                for i in range(int(acceptable_price) - 2, int(acceptable_price) - 2 - less - 1, -1):
                    vol = 10 if max_vol >= 10 else max_vol
                    print("BUY", str(-vol) + "x", i)
                    order_lst.append(Order(product, i, vol))
                    max_vol -= vol
            elif trade_made == "SELL":
                less = (max_vol+5)//6
                for i in range(int(acceptable_price) + 2, int(acceptable_price) + 2 + less):
                    vol = 10 if max_vol >= 10 else max_vol
                    print("SELL", str(vol) + "x", i)
                    order_lst.append(Order(product, i, -vol))
                    max_vol -= vol


    def get_expected_price(self, state: TradingState) -> Dict[str, float]:

      ret: Dict[str, float] = {}
      for product in state.order_depths.keys():              
        expected_val = 0
        total = 0

        buy_orders = state.order_depths[product].buy_orders
        sell_orders = state.order_depths[product].sell_orders
        
        exp_buy, total_buy = self._get_expected_total(buy_orders)
        exp_sell, total_sell = self._get_expected_total(sell_orders)

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

        day = state.timestamp
        current = ((day - 1) * 1_000_000) + self.current_iter
       

        # Iterate over all the keys (the available products) contained in the order depths
        for product in state.order_depths.keys():
            if product == "BANANAS":
                pos = state.position.get(product, 0)
                max_buy = 20 - pos
                max_sell= abs(-20 - pos)
                expected_val_tup = expected_val_dict[product]
                expected_val_total, expected_val_buy, expected_val_sell = expected_val_tup

                self.cache.pop()
                self.cache.append((current, expected_val_total))

                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]
                
                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                ## patel calls function gets model

                model = self._best_fit_line(self.cache)
                
                middle = model(current)

                self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= middle, trade_made="BUY", product=product, order_lst = orders)

                self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= middle, trade_made="SELL", product=product, order_lst = orders)

                result[product] = orders
            elif product == 'PEARLS':
                
                pos = state.position.get(product, 0)
                max_buy = min(20 - pos, 20)
                max_sell = min(abs(-20 - pos), 20)
                # Retrieve the Order Depth containing all the market BUY and SELL orders for PEARLS
                order_depth: OrderDepth = state.order_depths[product]


                # Initialize the list of Orders to be sent as an empty list
                orders: list[Order] = []

                # Define a fair value for the PEARLS.
                # Note that this value of 1 is just a dummy value, you should likely change it!
                acceptable_price = 10000

                # If statement checks if there are any SELL orders in the PEARLS market
                hadBOrder = False
                sell_keys_lst = sorted(order_depth.sell_orders.keys())
                for best_ask in sell_keys_lst:

                    # Sort all the available sell orders by their price,
                    # and select only the sell order with the lowest price
                    #best_ask = min(order_depth.sell_orders.keys())
                
                    # Check if the lowest ask (sell order) is lower than the above defined fair value
                    if best_ask < acceptable_price:
                        best_ask_volume = abs(order_depth.sell_orders[best_ask])
                        vol_to_trade = min(best_ask_volume, max_buy)
                        max_buy -= vol_to_trade
                        # In case the lowest ask is lower than our fair value,
                        # This presents an opportunity for us to buy cheaply
                        # The code below therefore sends a BUY order at the price level of the ask,
                        # with the same quantity
                        # We expect this order to trade with the sell order
                        print("BUY", str(-best_ask_volume) + "x", best_ask, end = "|")
                        orders.append(Order(product, best_ask, best_ask_volume))
                        hadBOrder = True
                    else: 
                        break
                    if max_buy <= 0:
                        break
                
                if max_buy > 0 and not hadBOrder:
                    less = (max_buy+9)//10
                    for i in range(10000 - 3, 10000 - 3 - less - 1, -1):
                        vol = 10 if max_buy >= 10 else max_buy
                        print("BUY", str(-vol) + "x", i, end = "|")
                        orders.append(Order(product, i, vol))
                        max_buy -= vol

                # The below code block is similar to the one above,
                # the difference is that it finds the highest bid (buy order)
                # If the price of the order is higher than the fair value
                # This is an opportunity to sell at a premium   
                hadSOrder = False
                buy_keys_lst = sorted(order_depth.buy_orders.keys(), reverse = True)
                for best_bid in buy_keys_lst:

                    # best_bid = max(order_depth.buy_orders.keys())

                    if best_bid > acceptable_price:
                        best_bid_volume = order_depth.buy_orders[best_bid]
                        vol_to_trade = min(best_bid_volume, max_sell)
                        max_sell -= vol_to_trade
                        print("SELL", str(vol_to_trade) + "x", best_bid, end= "|")
                        orders.append(Order(product, best_bid, -vol_to_trade))
                        hadSOrder = True
                    else:
                        break
                    if max_sell <= 0:
                        break
                
                if max_sell > 0 and not hadSOrder:
                    less = (max_sell+9)//10
                    for i in range(10000 + 3, 10000 + 3 + less):
                        vol = 10 if max_sell >= 10 else max_sell
                        print("SELL", str(vol) + "x", i, end= "|")
                        orders.append(Order(product, i, -vol))
                        max_sell -= vol
                # Add all the above orders to the result dict
                result[product] = orders
                print()

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