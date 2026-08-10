import numpy as np
import pandas as pd
import os
from sklearn import linear_model

lr = linear_model.LinearRegression()


factor_name = os.path.basename(__file__)[:-3]

univ = pd.read_pickle('./universe/stock_universe_filtered.pkl').reset_index()

result = []
for i in univ.values:
    data = pd.read_csv('./data/Order/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
    data = data[data.MDTime < 92600000000]
    data = data[(data.OrderType == 2) & (data.MDTime > 92000000000)].set_index('MDTime')
    if len(data) > 1:
        if len(data.loc[92300000000:]) > 1:
            data1 = data.copy()
            data1.OrderQty = data1.OrderQty * data1.OrderPrice * (data1.OrderBSFlag == 1)
            data2 = data.copy()
            data2.OrderQty = data2.OrderQty * data2.OrderPrice * (data2.OrderBSFlag == 2)
            temp = (data1.OrderQty.cumsum() - data2.OrderQty.cumsum()).loc[92300000000:].to_frame().reset_index()
            lr.fit(temp[['MDTime']], temp[['OrderQty']])
            result.append([i[0], i[1], (lr.predict(temp[['MDTime']]) - temp[['OrderQty']]).std().values[0]])

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

result.to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
