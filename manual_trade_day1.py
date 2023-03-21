trading_table = {
    'pizza':{'pizza': 1, 'root':0.5, 'snowball':1.45, 'shells':0.75},
    'root':{'pizza': 1.95, 'root':1, 'snowball':3.1, 'shells':1.49},
    'snowball':{'pizza': 0.67, 'root':0.31, 'snowball':1, 'shells':0.48},
    'shells':{'pizza': 1.34, 'root':0.64, 'snowball':1.98, 'shells':1},
                }

def recursive_decent(currency, val, profit, iter, path, max_iter):
    if iter < max_iter:
        pathTemp = path
        for currencies in trading_table[currency]:
            factor = trading_table[currency][currencies]
            new_val = val * factor
            string = str(iter) + ": converted " + str(val) + " " + currency + " to " + str(new_val) + " " + currencies + "\n"
            profitMaybe, string = recursive_decent(currencies, new_val, profit, iter + 1, path + string, max_iter)
            if profitMaybe > profit:
                profit = max(profitMaybe, profit)
                pathTemp = string
                
        return profit, pathTemp
    else:
        factor = trading_table[currency]['shells']
        new_val = val * factor
        string = str(iter) + ": converted " + str(val) + " " + currency + " to " + str(new_val) + " " + 'shells' + "\n"
        if new_val > profit:
            return max(profit, new_val), path + string
        else:
            return max(profit, new_val), path



def calculate_max_profit():
    shells = 2_000_000
    profit = 0
    path = ""
    # print(profit)
    tup = recursive_decent('shells', shells, 0, 0, "", 4)
    if profit < tup[0]:
        profit = max(profit,tup[0])
        #print(profit)
        path = tup[1]
    return profit, path

profit, path = calculate_max_profit()
print(profit)
print(path)