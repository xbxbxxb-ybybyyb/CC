import numpy as np
import pandas as pd
import os



factor_name = os.path.basename(__file__)[:-3]

univ = pd.read_pickle('./universe/stock_universe_filtered.pkl').reset_index()

result = []
for i in univ.values:
    data_order = pd.read_csv('./data/Order/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data_order['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order.dt]
    data_order = data_order[data_order.MDTime < 92600000000]
    
    if i[1][0] == '6':
        data_order_raw = pd.read_csv('./data/Order_RAW/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
        data_order_raw['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_order_raw.dt]
        data_order_raw = data_order_raw[data_order_raw.MDTime < 92600000000]
        result.append([i[0], i[1], -(data_order_raw.OrderQty * data_order_raw.OrderPrice)[data_order_raw.OrderType == 10].sum() / (data_order.OrderQty * data_order.OrderPrice).sum()])
    else:
        data_txn = pd.read_csv('./data/Transaction/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
        data_txn['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data_txn.dt]
        data_txn = data_txn[data_txn.MDTime < 92600000000]
        data_txn['indexJoin'] = data_txn.TradeBuyNo + data_txn.TradeSellNo
        data_txn = data_txn.set_index('indexJoin').join(data_order.rename(columns = {'OrderIndex':'indexJoin'}).set_index('indexJoin')[['OrderPrice']])
        result.append([i[0], i[1], -(data_txn.TradeQty * data_txn.OrderPrice)[data_txn.TradeType == 1].sum() / (data_order.OrderQty * data_order.OrderPrice).sum()])
        

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

result.to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
