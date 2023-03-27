import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datamodel import TradingState, OrderDepth
from round3.r3_trader import Trader
from math import isnan
from round3.r3submission import Trader


fileName = sys.argv[1]
print(fileName)
data = pd.read_csv(filepath_or_buffer=fileName, sep=';')

products = ['PEARLS']
productData = {p:data.query(f"product=='{p}'") for p in products}
buyTicks = {p: [] for p in products}
sellTicks = {p: [] for p in products}

state = TradingState(
	timestamp=0,
    listings={},
	order_depths={},
	own_trades={},
	market_trades={},
    position={},
    observations={}
)

trader = Trader()
iterations = len(productData[products[0]])
start, end = (0, 10000)
for i in range(start, end):
    print(f'-----Iteration {i}-----')
    orderDepths = {}
    state.observations['DOLPHIN_SIGHTINGS'] = dolphin_obs.iloc[i]['mid_price']
    for p in products:
        row = productData[p].iloc[i]
        state.timestamp = row['timestamp']
        buyOrders, sellOrders = {}, {}

        for j in range(1, 4):
            bidPrice, bidVolume = row[f'bid_price_{j}'], row[f'bid_volume_{j}']
            if not isnan(bidPrice) and not isnan(bidVolume):
                buyOrders[bidPrice] = bidVolume
            
            askPrice, askVolume = row[f'ask_price_{j}'], row[f'ask_volume_{j}']
            if not isnan(askPrice) and not isnan(askVolume):
                sellOrders[askPrice] = askVolume
        
        orders = OrderDepth()
        orders.buy_orders = buyOrders
        orders.sell_orders = sellOrders
        orderDepths[p] = orders
    
    state.order_depths = orderDepths
    result = trader.run(state=state)

    for p in products:
        profits[p].append(0 if len(profits[p]) == 0 else profits[p][-1])
        buyTicks[p].append(0)
        sellTicks[p].append(0)
        if p in result:
            for o in result[p]:
                if o.quantity > 0:
                    profits[p][-1] -= (o.quantity * o.price)
                    buyTicks[p][-1] = 1
                    state.position[p] = state.position.get(p, 0) + o.quantity
                elif o.quantity < 0:
                    profits[p][-1] += (abs(o.quantity) * o.price)
                    sellTicks[p][-1] = 1
                    state.position[p] = state.position.get(p, 0) - abs(o.quantity)

    print()

for p in products:
    bought = buyTicks[p]
    sold = sellTicks[p]
    profitLoss = data.query(f"product=='{p}'")['profit_and_loss'] 
    midPrices = data.query(f"product=='{p}'")['mid_price']
    times = data.query(f"product=='{p}'")['timestamp']

    buyMarkers = np.where(np.array(bought) == 1)[0]
    sellMarkers = np.where(np.array(sold) == 1)[0]
    print(buyMarkers)

    fig, ax1 = plt.subplots(dpi=95)
    fig.set_size_inches(16, 8)
    ax1.scatter(times, midPrices, s=0.1,label='Mid Prices')

    # Set the label and limits for the first Axes object
    ax1.set_xlabel('TimeStamps')
    ax1.set_ylabel(f'{p} Mid Price')
    ax1.set_ylim(midPrices.min(), midPrices.max())

    # plt.figure(figsize=(16, 8), dpi=88)
    # plt.subplots_adjust(left=0.05, bottom=0.05, right=0.95, top=0.95)
    plt.scatter(times, midPrices, s=0.1,label='Mid Prices')
    ax1.plot(np.array(times)[buyMarkers], np.array(midPrices)[buyMarkers], '^', markersize=4, color='blue', label='Buy Signal')
    ax1.plot(np.array(times)[sellMarkers], np.array(midPrices)[sellMarkers], 'v', markersize=4, color='orange', label='Sell Signal')

    ax2 = ax1.twinx()
    ax2.scatter(times, profitLoss, s=0.1, label='Profit/Loss', color='orange')

    ax2.set_ylabel('Profit/Loss')
    ax2.tick_params(axis='y')
    ax2.set_ylim(zscores.min(), zscores.max())

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')
    # lines, labels = ax1.get_legend_handles_labels()
    # lines2, labels2 = ax2.get_legend_handles_labels()
    # ax2.legend(lines + lines2, labels + labels2, loc='best')

    # plt.legend()
    plt.title(f'{p} Buy and Sell Signals')
    finalPNL = profits[p][-1]
    if state.position[p] < 0:
        finalPNL -= (abs(state.position[p]) * midPrices.tolist()[-1])
    elif state.position[p] > 0:
        finalPNL += (abs(state.position[p]) * midPrices.tolist()[-1])

    print(f'{p} had {len(buyMarkers)} Buy Signals')
    print(f'{p} had {len(sellMarkers)} Sell Signals')

plt.show()