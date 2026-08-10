from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 更优波动率的均值
class factor_717(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_717, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[data.TradeType == 0].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':['first','max','min','last'], 'TradeQty':'sum', 'TradeMoney':'sum'})
            dfmin.columns =  ['open', 'high', 'low', 'close', 'volume', 'amount']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'high', 'low', 'close']] = dfmin[['open', 'high', 'low', 'close']].fillna(method = 'ffill')

            price_data = dfmin[['open', 'high', 'low', 'close']].values.reshape(-1)
            dfmin['std20'] = pd.Series(price_data).rolling(window=20).std().values[3::4]
            dfmin['mean20'] = pd.Series(price_data).rolling(window=20).mean().values[3::4]
            dfmin['super_std'] = (dfmin['std20'] / dfmin['mean20']) ** 2
            factor[stk] = dfmin['super_std'].mean()*1e6
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T

        return factor