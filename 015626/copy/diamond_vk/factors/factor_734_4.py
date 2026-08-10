from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
import statsmodels.api as sm


# 朝没晨雾 方正10
class factor_734_4(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['close', 'volume']
        super(factor_734_4, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        close = df['close'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        volume = df['volume'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in volume.columns.tolist():
            dfmin = pd.concat([close[stk], volume[stk]], axis = 1)
            dfmin.columns = ['close', 'volume']
            if dfmin['volume'].sum() == 0:
                continue
                
            dfmin['ret'] = dfmin['close'].pct_change()
            dfmin['volume_diff'] = dfmin['volume'].diff()
            x_list = ['volume_diff']
            for i in range(1,6):
                dfmin[f'vdiff_{i}'] = dfmin['volume_diff'].shift(i)
                x_list.append(f'vdiff_{i}')
            dfmin = dfmin[6:]

            y = dfmin['ret'].fillna(0)
            X = dfmin[x_list].replace([np.inf, -np.inf], np.nan).fillna(0)
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()
            f = model.fvalue
            abs_intercept = abs(model.params[0])

            factor[stk] = [np.nanstd([model.params[i] for i in range(2,7)], ddof = 1)*1e10, f, abs_intercept*1e5]
        
        factor = pd.DataFrame(factor, index = ['factor_734_0', 'factor_734_1', 'factor_734_2']).T
        factor['factor_734_3'] = factor['factor_734_2']
        factor.loc[factor['factor_734_1'] < factor['factor_734_1'].mean(), 'factor_734_3'] = factor['factor_734_3'] * -1
        return factor