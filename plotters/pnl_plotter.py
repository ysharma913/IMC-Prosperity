import pandas as pd
import matplotlib.pyplot as plt

fileName = 'results/round2_results.csv'
data = pd.read_csv(filepath_or_buffer=fileName, sep=';')

bananaPrices = list(data.query("product=='BANANAS'")['profit_and_loss'])
pearlPrices = list(data.query("product=='PEARLS'")['profit_and_loss'])
coconutPrices = list(data.query("product=='COCONUTS'")['profit_and_loss'])
pinacoladaPrices = list(data.query("product=='PINA_COLADAS'")['profit_and_loss'])

times = data['timestamp'].unique()

plt.figure()
plt.plot(times, bananaPrices, zorder = -1)
plt.plot(times, pearlPrices, zorder = -1)
plt.figure()
plt.plot(times, coconutPrices, zorder = -1)
plt.plot(times, pinacoladaPrices, zorder = -1)
plt.show()


# max bannas 20, -20

# 0 -> 10, 
# 10 -> -30 
# -20

# get last 20 datapoints and try to trade