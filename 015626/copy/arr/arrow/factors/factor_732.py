from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 日跳跃度因子
class factor_732(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_732, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[(data.TradeType == 0) & (data.TradePrice > 0)].set_index('dt')

            amplitude = data.TradePrice.max() / data.TradePrice.min() - 1

            dfmin = data.resample('1min').agg({'TradePrice':['first','last']})
            dfmin.columns =  ['open', 'close']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'close']] = dfmin[['open', 'close']].fillna(method = 'ffill')

            dfmin['ret1'] = dfmin['close'].pct_change()
            dfmin['ret2'] = np.log(dfmin['close'] / dfmin['close'].shift())
            dfmin['ret_diff'] = dfmin['ret1'] - dfmin['ret2']
            dfmin['res'] = dfmin['ret_diff'] * 2 - dfmin['ret2'] ** 2
            
            factor[stk] = [dfmin['res'].mean(), amplitude]

        factor = pd.DataFrame(factor, index = ['res', self.__class__.__name__]).T
        factor.loc[factor['res'] < factor['res'].mean(), self.__class__.__name__] = factor[self.__class__.__name__] * -1
        factor = factor[[self.__class__.__name__]]

        return factor