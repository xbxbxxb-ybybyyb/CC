from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
import statsmodels.api as sm


# 朝没晨雾 方正10
class factor_734_4(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_734_4, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[(data.TradeType == 0) & (data.TradePrice > 0)].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':['first','last'], 'TradeQty':'sum'})
            dfmin.columns =  ['open', 'close', 'volume']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'close']] = dfmin[['open', 'close']].fillna(method = 'ffill')
            dfmin['volume'] = dfmin['volume'].fillna(0)
            
            dfmin['ret'] = dfmin['close'].pct_change()
            dfmin['volume_diff'] = dfmin['volume'].diff()
            x_list = ['volume_diff']
            for i in range(1,6):
                dfmin[f'vdiff_{i}'] = dfmin['volume_diff'].shift(i)
                x_list.append(f'vdiff_{i}')
            dfmin = dfmin.between_time('936', '1456')

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