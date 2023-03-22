import pandas as pd
from collections import deque
day_i_data = pd.read_csv('island-data-bottle-round-1/prices_round_1_day_0.csv', sep=';')
day_i_data = day_i_data[day_i_data['product'] == "BANANAS"]
day_i_data['timestamp'] -= max(day_i_data['timestamp'].values)

# min max mid
day_i_data = day_i_data.tail(2500)

tuple_lst = deque(zip(day_i_data['bid_price_1'], day_i_data['ask_price_1'], day_i_data['mid_price']))
print(tuple_lst)


