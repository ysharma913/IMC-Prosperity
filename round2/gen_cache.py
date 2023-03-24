import pandas as pd
def gen_cache(window_size):
  all_day_data = pd.DataFrame()
  last_timestamp = 0
  modulo = 1
  for i in range(3):
      day_i_data = pd.read_csv(f'../island-data-bottle-round-2/prices_round_2_day_{i-1}.csv', sep=';')
      day_i_data = day_i_data[day_i_data['product'] == "BANANAS"]
      day_i_data['timestamp'] += last_timestamp 
      all_day_data = pd.concat([all_day_data, day_i_data], axis=0)

      last_timestamp = day_i_data['timestamp'].iloc[-1] + 1

  # all_day_data = all_day_data[all_day_data['mid_price'] > 2000]
  all_day_data['timestamp'] -= (all_day_data['timestamp'].iloc[-1] +100)
  all_day_data = all_day_data[all_day_data['timestamp'] % (modulo * 100) == 0]
  all_day_data = all_day_data.tail(window_size)



  with open('cache.txt', 'w') as f:
      tup = tuple(zip(all_day_data['timestamp'], all_day_data['mid_price']))
      print(len(tup))
      f.write(str(tup))

if __name__ == '__main__':
   gen_cache(150)
