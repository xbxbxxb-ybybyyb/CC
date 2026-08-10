from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 日跳跃度因子
class t_factor_731(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction']
        super(t_factor_731, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[data.TradeType == 0].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':['first','last']})
            dfmin.columns =  ['open', 'close']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'close']] = dfmin[['open', 'close']].fillna(method = 'ffill')

            dfmin['ret1'] = dfmin['close'].pct_change()
            dfmin['ret2'] = np.log(dfmin['close'] / dfmin['close'].shift())
            dfmin['ret_diff'] = dfmin['ret1'] - dfmin['ret2']
            dfmin['res'] = dfmin['ret_diff'] * 2 - dfmin['ret2'] ** 2
            
            factor[stk] = dfmin['res'].mean() * 1e8

        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T

        return factor