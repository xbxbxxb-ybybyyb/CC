import numpy as np
import pandas as pd
import os



factor_name = os.path.basename(__file__)[:-3]

univ = pd.read_pickle('./universe/stock_universe_filtered.pkl').reset_index()

result = []
for i in univ.values:
    data = pd.read_csv('./data/Transaction/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data = data[data.TradeType == 0]
    data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
    data = data[data.MDTime < 92600000000]
    data = data.groupby('TradeBuyNo').sum()[['TradeQty']]
    result.append([i[0], i[1], (data[data.gt(data.quantile(0.9, axis = 0))].sum()/data.sum()).values[0]])

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

result.to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
