# Open the original file for reading
file_name = 'island-data-bottle-round-3/prices_round_3_day_2.csv'
with open(file_name, 'r') as f:
    # Open a new file for writing
    with open("berries-prices_round_3_day_2.csv", 'w') as f_out:
        # Write the header row to the new file
        header = f.readline()
        f_out.write(header)
        
        # Loop over the remaining rows in the original file
        for line in f:
            # Check if the line contains "BERRIES"
            if "BERRIES" in line:
                # If it does, write the line to the new file
                f_out.write(line)
