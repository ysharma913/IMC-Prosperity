import matplotlib.pyplot as plt
import numpy as np

def extract_data(filename, products, plots):
    data = {p: [] for p in products}
    offers = {}
    for p in plots:
        for prod in products:
            offers[f'{prod} {p}'] = []
    
    with open(filename, 'r') as f:
        for line in f:
            if 'Bid Quantity' in line or 'Ask Quantity' in line or 'Mid Price' in line:
                tokens = line.strip().split(': ')
                offers[tokens[0]].append(int(float(tokens[1])))
            else:
                fields = line.strip().split(';')
                if len(fields) < 17:
                    continue
                if fields[2] in products:
                    try:
                        profit_and_loss = float(fields[-1])
                        data[fields[2]].append(profit_and_loss)
                    except ValueError:
                        pass
    return data, offers

products = ['BANANAS', 'PEARLS', 'COCONUTS', 'PINA_COLADAS']
plots = ['Bid Quantity', 'Ask Quantity', 'Mid Price']
file_name = "round2logs/acafa98f-3226-44e9-92e2-d4394881f218.log"
data, volumes = extract_data(filename=file_name, products=products, plots=plots)

# volumes['TotalVolume'] = list(np.add(np.add(volumes['OwnBuyVolume'], volumes['OwnSellVolume']), (volumes['MarketVolume'])))

for prod in products:
    volumes[f'{prod} Diff'] = np.subtract(volumes[f'{prod} Bid Quantity'], volumes[f'{prod} Ask Quantity'])

# Plot the profit and loss values for each product on the same graph
plt.figure(figsize=(8,6))
for p in products:
    plt.plot(data[p], label=p)
plt.legend()
plt.xlabel('Data Point')
plt.ylabel('Profit and Loss')
plt.title('Profit and Loss for Different Products')

for prod in products:
    plt.figure(figsize=(8, 6))
    plt.plot(volumes[f'{prod} Diff'], label=f'{prod} Diff')
    # for p in plots:
    #     if p != 'Mid Price':
    #         plt.plot(volumes[f'{prod} {p}'], label=f'{prod} {p}')
    
    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Offers and Price')
    plt.title('Offers and Price over Time')
plt.show()