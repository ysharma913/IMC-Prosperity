import pandas as pd
import matplotlib.pyplot as plt 
import numpy as np


def _test_best_fit_line(func):
    all_day_data = pd.DataFrame()
    last_timestamp = 0
    for i in range(3):
        day_i_data = pd.read_csv(f'../island-data-bottle-round-2/prices_round_2_day_{i-1}.csv', sep=';')
        day_i_data = day_i_data[day_i_data['product'] == "BANANAS"]
        day_i_data['timestamp'] += last_timestamp 
        all_day_data = pd.concat([all_day_data, day_i_data], axis=0)

        last_timestamp = day_i_data['timestamp'].iloc[-1] + 1

    all_day_data = all_day_data[all_day_data['mid_price'] > 2000]
    all_day_data['timestamp'] -= all_day_data['timestamp'].iloc[-1]


    myline = np.linspace(all_day_data['timestamp'].iloc[0], all_day_data['timestamp'].iloc[-1], 200)
    plt.scatter(all_day_data['timestamp'], all_day_data['mid_price'])

    all_points_tup = tuple(zip(all_day_data['timestamp'], all_day_data['mid_price']))
    

    window_size = 1000
    step_size = 100

    window = all_points_tup[0: window_size]

    for i in range(window_size, len(all_points_tup)):
      model = func(window)
      myline = np.linspace(window[0][0], window[-1][0], 400)

      window = all_points_tup[i - window_size + 1: i]
      plt.plot(myline, model(myline), 'r-')


        

    # for i in range(all_day_data['timestamp'].iloc[0], all_day_data['timestamp'].iloc[-1], window_size * step_size):
    #     start, stop = i, i + window_size * step_size
    #     partial_data = all_day_data[(all_day_data['timestamp'] >= start) & (all_day_data['timestamp'] < stop)]
    #     model = func(tuple(zip(partial_data['timestamp'], partial_data['price'])))
    #     myline = np.linspace(start, stop, window_size)
    #     plt.plot(myline, model(myline), 'r-')
    # # plt.plot(myline, model(myline), markerfacecolor='red')
    
    plt.show()

  
