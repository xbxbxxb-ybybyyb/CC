import numpy as np
import pandas as pd
import os



factor_name = os.path.basename(__file__)[:-3]

univ = pd.read_pickle('./universe/stock_universe_filtered.pkl').reset_index()

result = []
for i in univ.values:
    data_tick = pd.read_csv('./data/Stock/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data_tick['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_tick.dt]
    data_tick = data_tick[data_tick.MDTime < 92600000000]
    data_order = pd.read_csv('./data/Order/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data_order['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order.dt]
    data_order = data_order[data_order.MDTime < 92600000000]
    
    if (len(data_order) > 1) & (len(data_tick) > 1):
        MinPx = data_tick['MinPx'].values[0]
        data_order = data_order[(data_order.OrderType == 2) & (data_order.OrderBSFlag == 2) & (data_order.MDTime > 92000000000)]
        if len(data_order) > 1:
            MinPxOrder = data_order[data_order.OrderPrice == MinPx].OrderQty.sum()
            totalOrder = data_order.OrderQty.sum()
        
            result.append([i[0], i[1], -MinPxOrder/totalOrder])

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

result.to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
