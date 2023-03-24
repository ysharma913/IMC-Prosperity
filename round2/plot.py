import matplotlib.pyplot as plt

def get_nextln(data: str):
  prevnl = -1
  while True:
    nextnl = data.find('\n', prevnl + 1)
    # print(nextnl)
    if nextnl < 0: break

    # print(data[prevnl + 1:nextnl])
    split_data = data[prevnl + 1:nextnl].split(':')

    if(split_data[0] == 'FOR_PLOT'):
      yield split_data
    
    prevnl = nextnl

    

def plot(log_file):
  with open (log_file, 'r') as f:
    data = f.read()

  # data = "a\nFOR_PLOT:TRUE_MID:0.5:MAX_BUY:10:MIN_ASK:11:PRED_MIDDLE:4816.965955171957\n"
  
  points = list(get_nextln(data=data))

  # print(points, '\ln')
  times, true_mids, max_buys, min_asks, pred_mids = [], [], [], [], []
  buy_times, buy_prices = [], []
  sell_times, sell_prices = [], []


  min_pred = 4860
  for p in points:
    time = float(p[2])
    times.append(time)
    true_mids.append(float(p[4]))
    max_buys.append(float(p[6]))
    min_asks.append(float(p[8]))
    pred = float(p[10])
    pred_mids.append(pred if pred > min_pred else min_pred)

    buy_price = p[12]
    # print(buy_price)
    if buy_price != 'None':
      buy_times.append(time)
      buy_prices.append(float(buy_price))
    
    sell_price = p[14]
    if sell_price != 'None':
      print(sell_price)
      sell_times.append(time)
      sell_prices.append(float(sell_price))



  # plt.scatter(times, max_buys, s = 1)
  # plt.scatter(times, min_asks, s = 1)
  # plt.scatter(times, pred_mids, s=1)
  # plt.scatter(times, true_mids, s=1)

  

  plt.plot(times, max_buys, linestyle = 'dashed', linewidth=1, zorder = -1)
  plt.plot(times, min_asks, linestyle = 'dashed', linewidth=1, zorder = -1)
  plt.plot(times, pred_mids, linestyle = 'dashed', linewidth=1, zorder = -1)
  plt.plot(times, true_mids, linestyle = 'dashed', linewidth=1, zorder = -1)

  plt.scatter(buy_times, buy_prices, c = 'black', s = 20, zorder = 1)
  plt.scatter(sell_times, sell_prices, c = 'black', s = 20, zorder = 1)

  
  plt.show()




if __name__ == '__main__':
  plot('plotting_data.log')
    

    