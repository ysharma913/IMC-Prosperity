from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade, Listing
from collections import deque
import operator
import numpy as np
import math, statistics
import pandas as pd


class Trader:

    initalizedStart = False
    limits = {'PEARLS': 20, 'BANANAS': 20, 'COCONUTS': 600, 'PINA_COLADAS': 300}
    regressions = {}

    def initData(self):
        self.initalizedStart = True
        self.regressions['PEARLS'] = []
        self.regressions['BANANAS'] = []

        self.regressions['COCONUTS'] = []
        self.regressions['PINA_COLADAS'] = []
    
    def calculate_spread(self):
        coconuts = np.array(self.regressions['COCONUTS'])
        coladas = np.array(self.regressions['PINA_COLADAS'])

        ratio = pd.Series(coladas/coconuts)

        ratios_mavg5 = ratio.rolling(window=5, center=False).mean()
        ratios_mavg20 = ratio.rolling(window=20, center=False).mean()
        std_20 = ratio.rolling(window=20, center=False).std()
        zscore_20_5 = (ratios_mavg5 - ratios_mavg20)/std_20

        return zscore_20_5.iloc[-1]

    def marketmake(self, product, tradeMade, quantity, acceptablePrice, volume, orderList):
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

    def getProductValue(self, product, currPrice):
        self.regressions[product] = self.regressions[product][1:] + [currPrice]
        model = np.poly1d(np.polyfit(np.arange(1, len(self.regressions[product])+1), np.array(self.regressions[product]), 1))
        return model(len(self.regressions[product]))

    def do_order(self, bot_orders, operator, max_vol, acceptable_price, trade_made, product, order_lst):
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

    def do_midpoint(self, sell_orders, buy_orders):
        return (min(sell_orders) + max(buy_orders)) / 2
    
    def run(self, state: TradingState) -> Dict[str, List[Order]]:

        # 500, z_thresh = 1.25
        WINDOW_SIZE = 500
        if not self.initalizedStart:
            self.initData()
        
        z_thresh = 1.25
        result = {}
        for product in state.order_depths.keys():
            pos = state.position.get(product, 0)
            limit = self.limits[product]
            max_buy = limit - pos
            max_sell = abs(-limit - pos)
            order_depth: OrderDepth = state.order_depths[product]
            orders: list[Order] = []

            if product == "COCONUTS":

                product_pina = "PINA_COLADAS"
                pina_pos = state.position.get(product_pina, 0)
                pina_limit = self.limits[product_pina]
                max_buy_pina = pina_limit- pina_pos
                max_sell_pina= abs(-pina_limit- pina_pos)
                

                pina_orders: list[Order] = []
                pina_order_depth: OrderDepth = state.order_depths[product_pina]


                # append to regressions:
                coconut_midpoint = self.do_midpoint(order_depth.sell_orders, order_depth.buy_orders)
                colada_midpoint =  self.do_midpoint(pina_order_depth.sell_orders, pina_order_depth.buy_orders)
                self.regressions[product].append(coconut_midpoint)
                self.regressions[product_pina].append(colada_midpoint)

                z_score = self.calculate_spread()

                print("Timestamp", state.timestamp)
                if state.timestamp/100 >= WINDOW_SIZE:
              
                    # need to figure out how many pina coladas to buy?
                    print("z-score", z_score)
                    if z_score > z_thresh:
                        print("BUYING BOTH")
                        self.do_order(bot_orders = pina_order_depth.sell_orders, operator = operator.lt, max_vol = max_buy_pina, acceptable_price= 1000000, trade_made="BUY", product=product_pina, order_lst = pina_orders)

                        self.do_order(bot_orders = order_depth.sell_orders, operator = operator.lt, max_vol = max_buy, acceptable_price= 1000000, trade_made="BUY", product=product, order_lst = orders)

                    elif z_score < -z_thresh:
                        print("SELLING BOTH")
                        self.do_order(bot_orders = pina_order_depth.buy_orders, operator = operator.gt, max_vol = max_sell_pina, acceptable_price= 0, trade_made="SELL", product=product_pina, order_lst = pina_orders)

                        self.do_order(bot_orders = order_depth.buy_orders, operator = operator.gt, max_vol = max_sell, acceptable_price= 0, trade_made="SELL", product=product, order_lst = orders)
                
                result[product] = orders
                result[product_pina] = pina_orders

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
