import pandas as pd

fileName = 'island-data-bottle-round-2/prices_round_2_day_1.csv'
df = pd.read_csv(fileName, header='infer', sep=';')

bananaPrices = list(df.query("product=='BANANAS'")['mid_price'])[-3000:]
pearlPrices = list(df.query("product=='PEARLS'")['mid_price'])[-500:]
coconutPrices = list(df.query("product=='COCONUTS'")['mid_price'])[-3000:]
pinacoladaPrices = list(df.query("product=='PINA_COLADAS'")['mid_price'])[-3000:]

print(len(bananaPrices))
print(len(pearlPrices))
print(len(coconutPrices))
print(len(pinacoladaPrices))

with open('round2history.txt', 'w') as f:
    f.write('[' + ', '.join(map(str, bananaPrices)) + ']')
    f.write('\n\n')
    f.write('[' + ', '.join(map(str, pearlPrices)) + ']')
    f.write('\n\n')
    f.write('[' + ', '.join(map(str, coconutPrices)) + ']')
    f.write('\n\n')
    f.write('[' + ', '.join(map(str, pinacoladaPrices)) + ']')
    f.write('\n\n')