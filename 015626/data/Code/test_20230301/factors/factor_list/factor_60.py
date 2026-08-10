import numpy as np
import pandas as pd
import os



factor_name = os.path.basename(__file__)[:-3]

univ = pd.read_pickle('./universe/stock_universe_filtered.pkl').reset_index()

result = []
for i in univ.values:
    data = pd.read_csv('./data/Stock/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
    data['MDTime'] = [int(pd.Timestamp(x).strftime('%H%M%S%f')) for x in data.dt]
    data = data[data.MDTime < 92600000000]
    if len(data) > 1:
        
        b5amt = data.Buy1Price.values[-1] * data.Buy1OrderQty.values[-1] +\
                data.Buy2Price.values[-1] * data.Buy2OrderQty.values[-1] +\
                data.Buy3Price.values[-1] * data.Buy3OrderQty.values[-1] +\
                data.Buy4Price.values[-1] * data.Buy4OrderQty.values[-1] +\
                data.Buy5Price.values[-1] * data.Buy5OrderQty.values[-1] +\
                data.Buy6Price.values[-1] * data.Buy6OrderQty.values[-1] +\
                data.Buy7Price.values[-1] * data.Buy7OrderQty.values[-1] +\
                data.Buy8Price.values[-1] * data.Buy8OrderQty.values[-1] +\
                data.Buy9Price.values[-1] * data.Buy9OrderQty.values[-1] +\
                data.Buy10Price.values[-1] * data.Buy10OrderQty.values[-1]
        s5amt = data.Sell1Price.values[-1] * data.Sell1OrderQty.values[-1] +\
                data.Sell2Price.values[-1] * data.Sell2OrderQty.values[-1] +\
                data.Sell3Price.values[-1] * data.Sell3OrderQty.values[-1] +\
                data.Sell4Price.values[-1] * data.Sell4OrderQty.values[-1] +\
                data.Sell5Price.values[-1] * data.Sell5OrderQty.values[-1] +\
                data.Sell6Price.values[-1] * data.Sell6OrderQty.values[-1] +\
                data.Sell7Price.values[-1] * data.Sell7OrderQty.values[-1] +\
                data.Sell8Price.values[-1] * data.Sell8OrderQty.values[-1] +\
                data.Sell9Price.values[-1] * data.Sell9OrderQty.values[-1] +\
                data.Sell10Price.values[-1] * data.Sell10OrderQty.values[-1]
                
        result.append([i[0], i[1], b5amt / s5amt])

result = pd.DataFrame({'dt':np.array(result)[:,0], 'Ticker':np.array(result)[:,1], factor_name:np.array(result)[:,2]}).set_index(['dt', 'Ticker']).sort_index().astype(float)

result.to_pickle('./factors/factor_raw/' + factor_name + '.pkl')
