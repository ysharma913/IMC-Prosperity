import re
import matplotlib.pyplot as plt

file = 'd8935726-a838-45bd-9185-a307ce23e854.log'
product = ''

iterations = []
min_asks = []
max_bids = []
midpoints = []
flood_buys = set()
flood_sells = set()

with open("logs/" + file, "r") as f:
    for line in f:
        if line.startswith("Product:"):
            product = line.split(":")[1].strip()
        elif re.search("Iteration:\s+\d+", line):
            iteration = int(re.findall("Iteration:\s+(\d+)", line)[0])
            iterations.append(iteration)
        elif "Min ask :" in line:
            min_ask = int(line.split(":")[1].strip())
            min_asks.append(min_ask)
        elif "Max bid :" in line:
            max_bid = int(line.split(":")[1].strip())
            max_bids.append(max_bid)
        elif "Midpoint :" in line:
            midpoint = float(line.split(":")[1].strip())
            midpoints.append(midpoint)
        elif "FLOOD BUY" in line:
            if iteration not in flood_buys:
                flood_buys.add(iteration)
        elif "FLOOD SELL" in line:
            if iteration not in flood_sells:
                flood_sells.add(iteration)

fig, ax = plt.subplots()

# Plot lines
ax.plot(iterations, min_asks, label="Min Ask")
ax.plot(iterations, max_bids, label="Max Bid")
ax.plot(iterations, midpoints, label="Midpoint")

# Plot vertical lines for flood buys and sells
for iteration in flood_buys:
    ax.axvline(x=iteration, color="green", linestyle="--", alpha=0.2)
for iteration in flood_sells:
    ax.axvline(x=iteration, color="red", linestyle="--", alpha=0.2)

# Set title and labels
ax.set_title(f"{product} Prices")
ax.set_xlabel("Iteration")
ax.set_ylabel("Price")

# Add legend
ax.legend()

plt.show()