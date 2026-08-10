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
        data = data_order.set_index('MDTime')\
        .join(pd.DataFrame({'MDTime':np.arange(91500000000, 92500000000, 10000)}).set_index('MDTime')\
        .join(data_order.set_index('MDTime'))\
        .join(data_tick[['MDTime', 'Buy1Price']].set_index('MDTime'))\
        .fillna(method = 'ffill').dropna(subset = ['Buy1Price'])[['Buy1Price']]).drop_duplicates()
        
    
        b = data[(data.OrderPrice>data.Buy1Price) & (data.OrderBSFlag == 1)].OrderQty.sum()
        s = data[(data.OrderPrice<data.Buy1Price) & (data.OrderBSFlag == 2)].OrderQty.sum()
        
        if b + s > 0:
            result.append([i[0], i[1], -b/(b+s)])

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

result.to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
