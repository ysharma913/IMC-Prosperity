import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datamodel import TradingState, OrderDepth
from round2.brokenpairs import Trader
from math import isnan

fileName = 'results/round2_results.csv'
data = pd.read_csv(filepath_or_buffer=fileName, sep=';')

products = ['COCONUTS', 'PINA_COLADAS']
productData = {p:data.query(f"product=='{p}'") for p in products}
profits = {p: [] for p in products}
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
for i in range(iterations):
    print(f'-----Iteration {i}')
    orderDepths = {}
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
        buyTicks[p].append(0)
        sellTicks[p].append(0)
        if p in result:
            for o in result[p]:
                if o.quantity > 0:
                    buyTicks[p][-1] = 1
                    state.position[p] = state.position.get(p, 0) + o.quantity
                elif o.quantity < 0:
                    sellTicks[p][-1] = 1
                    state.position[p] = state.position.get(p, 0) - abs(o.quantity)
    print()

for p, q in [('COCONUTS', 'PINA_COLADAS')]:
    bought = buyTicks[p]
    sold = sellTicks[p]

    boughtPina = buyTicks[q]
    soldPina = sellTicks[q]

    midPrices = data.query(f"product=='{p}'")['mid_price']
    times = data.query(f"product=='{p}'")['timestamp']

    midPricesPina = data.query(f"product=='{q}'")['mid_price']

    buyMarkers = np.where(np.array(bought) == 1)[0]
    sellMarkers = np.where(np.array(sold) == 1)[0]

    buyMarkersPina = np.where(np.array(boughtPina) == 1)[0]
    sellMarkersPina = np.where(np.array(soldPina) == 1)[0]

    fig, ax1 = plt.subplots(dpi=95)
    fig.set_size_inches(16, 8)
    ax1.scatter(times, midPrices, s=0.1,label='Mid Prices', color='blue')

    # Set the label and limits for the first Axes object
    ax1.set_xlabel('TimeStamps')
    ax1.set_ylabel(f'{p} Mid Price')
    ax1.set_ylim(midPrices.min(), midPrices.max())
    ax1.plot(np.array(times)[buyMarkers], np.array(midPrices)[buyMarkers], '^', markersize=4, color='g', label=f'{p} Buy Signal')
    ax1.plot(np.array(times)[sellMarkers], np.array(midPrices)[sellMarkers], 'v', markersize=4, color='r', label=f'{p} Sell Signal')

    ax2 = ax1.twinx()
    ax2.scatter(times, midPricesPina, s=0.1,label='Mid Prices', color='teal')

    # Set the label and limits for the first Axes object
    ax2.set_xlabel('TimeStamps')
    ax2.set_ylabel(f'{q} Mid Price')
    ax2.set_ylim(midPricesPina.min(), midPricesPina.max())
    ax2.plot(np.array(times)[buyMarkersPina], np.array(midPricesPina)[buyMarkersPina], '^', markersize=4, color='orange', label=f'{q} Buy Signal')
    ax2.plot(np.array(times)[sellMarkersPina], np.array(midPricesPina)[sellMarkersPina], 'v', markersize=4, color='yellow', label=f'{q} Sell Signal')

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.title(f'{p} {q} Buy and Sell Signals')

    print(f'{p} had {len(buyMarkers)} Buy Signals')
    print(f'{p} had {len(sellMarkers)} Sell Signals')

plt.show()