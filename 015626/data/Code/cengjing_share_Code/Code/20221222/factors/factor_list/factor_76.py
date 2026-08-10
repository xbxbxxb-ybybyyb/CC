import numpy as np
import pandas as pd
import os



factor_name = os.path.basename(__file__)[:-3]

univ = pd.read_pickle('./universe/stock_universe_filtered.pkl').reset_index()

result = []
for i in univ.values:
    data_txn = pd.read_csv('./data/Transaction/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data_txn['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_txn.dt]
    data_txn = data_txn[(data_txn.MDTime < 92600000000) & (data_txn.TradePrice > 0)]
    data_order = pd.read_csv('./data/Order/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data_order['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order.dt]
    data_order = data_order[data_order.MDTime < 92600000000]
    
    if (len(data_order) > 0) & (len(data_txn) > 0):
        px = data_txn.TradePrice.values[-1]
        b = data_order[(data_order.OrderBSFlag == 1) & (data_order.OrderPrice >= px)]
        
        result.append([i[0], i[1], ((b.OrderPrice - px)*b.OrderQty).sum()])

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

(-result).to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
