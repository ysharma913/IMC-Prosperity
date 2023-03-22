import pandas as pd
from collections import deque
day_i_data = pd.read_csv('island-data-bottle-round-1/prices_round_1_day_0.csv', sep=';')
day_i_data = day_i_data[day_i_data['symbol'] == "BANANAS"]
day_i_data['timestamp'] -= max(day_i_data['timestamp'].values)

tuple_lst = deque(day_i_data['price'].tail(5000))
print(tuple_lst)


