import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.sarimax import SARIMAX
from pmdarima.arima import auto_arima

# Read in the CSV files as a list of Pandas dataframes
file_names = ['island-data-bottle-round-3/prices_round_3_day_0.csv', 'island-data-bottle-round-3/prices_round_3_day_1.csv', 'island-data-bottle-round-3/prices_round_3_day_2.csv']
data_frames = [pd.read_csv(file, sep=';') for file in file_names]

# Concatenate the dataframes into a single dataframe
data = pd.concat(data_frames)

# Extract the mid-price column
mid_price = data['mid_price']

# Determine the appropriate SARIMA parameters using auto_arima
model = auto_arima(mid_price, seasonal=True, m=4, max_order=None,
                   suppress_warnings=True, stepwise=True)

# Print the summary of the final model fit
print(model.summary())