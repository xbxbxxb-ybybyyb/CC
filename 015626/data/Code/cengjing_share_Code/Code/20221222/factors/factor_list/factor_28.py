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
    data = data[(data.OrderType == 2) & (data.OrderBSFlag == 2)]
    if len(data) > 1:
        lr.fit(data[['MDTime']], data[['OrderPrice']])
        result.append([i[0], i[1], (lr.predict(data[['MDTime']]) - data[['OrderPrice']]).std().values[0]])

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

result.to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
