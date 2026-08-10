from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 下午模糊性与上午模糊性之比
class factor_727(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_727, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[data.TradeType == 0].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':['first','max','min','last'], 'TradeQty':'sum', 'TradeMoney':'sum'})
            dfmin.columns =  ['open', 'high', 'low', 'close', 'volume', 'amount']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'high', 'low', 'close']] = dfmin[['open', 'high', 'low', 'close']].fillna(method = 'ffill')

            dfmin['ret'] = dfmin['close'].pct_change()
            dfmin['vol'] = dfmin['ret'].rolling(5, min_periods = 5).std()
            dfmin['vol_vol'] = dfmin['vol'].rolling(5, min_periods = 5).std()

            if dfmin.between_time('930', '1130')['vol_vol'].mean() == 0:
                factor[stk] = np.nan
            else:
                factor[stk] = dfmin.between_time('1300', '1456')['vol_vol'].mean() / dfmin.between_time('930', '1130')['vol_vol'].mean() - 1

        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T

        return factor