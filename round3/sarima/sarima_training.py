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

# Specify the size of the training and testing sets
train_size = int(len(mid_price) * 0.8)
test_size = len(mid_price) - train_size

# Iterate over the data and train the model on each training set
# and test it on the corresponding test set, updating the model
# parameters based on the new data
model = None
for i in range(train_size, len(mid_price), test_size):
    train_data = mid_price[:i]
    test_data = mid_price[i:i+test_size]

    # Determine the appropriate SARIMA parameters using auto_arima
    if model is None:
        model = auto_arima(train_data, seasonal=True, m=4, max_order=None,
                           suppress_warnings=True, stepwise=True)
    else:
        model.fit(train_data)
    
    # Forecast the test data using the fitted model
    forecast = model.predict(start=test_data.index[0], end=test_data.index[-1])

    # Evaluate the model's performance on the test data
    mse = ((forecast - test_data) ** 2).mean()
    print(f'Test MSE: {mse}')

    # Update the model parameters based on the new data
    if i + test_size < len(mid_price):
        model.update(test_data)

# Print the summary of the final model fit
print(model.summary())
