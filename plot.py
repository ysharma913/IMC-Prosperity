import matplotlib.pyplot as plt
import re

# Open the file for reading
file_name = "5ac99c2f-7f01-44a5-b2cd-4e5200d2038f.log"
banana_values = []
with open("logs/" + file_name, 'r') as file:
    # Loop through each line in the file
    for line in file:
        if re.match(r"\d+;\d+;BANANAS;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;.*;(\d+\.\d+);.*", line):
            matches = re.findall(r"\d+\.\d+", line)
            banana_value = float(matches[-1])
            banana_values.append(banana_value)


# Plot the banana values using Matplotlib
plt.plot(banana_values)
plt.title('Banana Values')
plt.xlabel('Row')
plt.ylabel('Float Value')
plt.show()

expected_vals = []

# Open the file and read line by line
with open("logs/" + file_name, 'r') as f:
    for line in f:
        # Extract expected_val using regular expression
        match = re.search(r'expected_val\s([\d\.]+)', line)
        if match:
            expected_val = float(match.group(1))
            expected_vals.append(expected_val)

# Create a plot of the expected_val values
plt.plot(expected_vals)
plt.xlabel('Index')
plt.ylabel('Expected Value')
plt.title('Expected Value Plot')
plt.show()