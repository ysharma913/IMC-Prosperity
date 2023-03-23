import matplotlib.pyplot as plt

# process input_file.txt
file_name1 = "d8935726-a838-45bd-9185-a307ce23e854.log"
file_name2 = "675a1e17-01c1-442c-ad03-9b8daa9e4854.log"
import matplotlib.pyplot as plt

def extract_info_from_file(filename):
    mid_prices = []
    flood_buys = []
    flood_sells = []

    with open(filename, 'r') as f:
        lines = f.readlines()

        for i in range(len(lines)):
            if "Iteration: " in lines[i]:
                print(lines[i].split())
                index = lines[i].split().index('Iteration:')
                iteration = int(lines[i].split()[index + 1])
                mid_price = float(lines[i+5].split()[2])
                mid_prices.append(mid_price)

                for j in range(len(lines[i+8:i+8+6])):
                    if "FLOOD BUY" in lines[i+8:i+8+6][j]:
                        flood_buys.append(iteration)
                    elif "FLOOD SELL" in lines[i+8:i+8+6][j]:
                        flood_sells.append(iteration)
    print(mid_prices)
    return mid_prices, flood_buys, flood_sells

file1 = "logs/d8935726-a838-45bd-9185-a307ce23e854.log"
file2 = "logs/675a1e17-01c1-442c-ad03-9b8daa9e4854.log"

# Extract information from both files
file1_mid_prices, file1_flood_buys, file1_flood_sells = extract_info_from_file(file1)
file2_mid_prices, file2_flood_buys, file2_flood_sells = extract_info_from_file(file2)

# Plotting
fig, ax = plt.subplots(figsize=(12,8))

# Plot mid_prices from input_file1
ax.plot(file1_mid_prices, label='Input File 1 Mid-Prices')

# Plot vertical lines on input_file1
for iteration in file1_flood_buys:
    ax.axvline(x=iteration, color='green', linestyle='--', alpha=0.5)
for iteration in file1_flood_sells:
    ax.axvline(x=iteration, color='red', linestyle='--', alpha=0.5)

# Plot mid_prices from input_file2
ax.plot(file2_mid_prices, label='Input File 2 Mid-Prices')

# Plot vertical lines on input_file2
total_green_buys = 0 
total_red_buys = 0
total_green_sells = 0 
total_red_sells = 0
for i in range(len(file2_flood_buys)):
        iteration = file2_flood_buys[i]
        if i < len(file2_mid_prices)-1:
            if (file2_mid_prices[i+1] - file2_mid_prices[i]) < (file1_mid_prices[i+1] - file1_mid_prices[i]):
                ax.axvline(x=iteration, color='green', linestyle='--', alpha=0.5)
                total_green_buys += 1
            else:
                ax.axvline(x=iteration, color='red', linestyle='--', alpha=0.5)
                total_red_buys += 1
 
for i in range(len(file2_flood_sells)):
        iteration = file2_flood_sells[i]
        if i < len(file2_mid_prices)-1:
            if (file2_mid_prices[i+1] - file2_mid_prices[i]) > (file1_mid_prices[i+1] - file1_mid_prices[i]):
                ax.axvline(x=iteration, color='red', linestyle='--', alpha=0.5)
                total_red_sells += 1
            else:
                ax.axvline(x=iteration, color='green', linestyle='--', alpha=0.5)
                total_green_sells += 1

print("total_green_sells: ", total_green_sells)
print("total_green_buys: ", total_green_buys)
print("total_red_sells: ", total_red_sells)
print("total_red_buys: ", total_red_buys)

total_green = total_green_buys + total_green_sells
total_red = total_red_buys + total_red_sells
print("percent: ", total_green / (total_red + total_green))
# Set axis labels and title
ax.set_xlabel('Iteration')
ax.set_ylabel('Mid-Price')
ax.set_title('Product Mid-Prices for Input File 1 and Input File 2')

# Add legend
ax.legend()

# Display the plot
plt.show()
