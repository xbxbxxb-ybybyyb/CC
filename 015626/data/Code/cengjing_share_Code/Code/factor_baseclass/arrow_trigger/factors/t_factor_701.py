from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 适度日耀眼波动率
class t_factor_701(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction']
        super(t_factor_701, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[data.TradeType == 0].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':'last', 'TradeQty':'sum'})
            dfmin.columns =  ['close', 'volume']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['close'])

            dfmin['ret'] = dfmin.close.pct_change()
            dfmin['std_next5'] = dfmin['ret'].rolling(5).std().shift(-4)

            dfmin['vdiff'] = dfmin.volume.diff()
            dfmin['vs'] = dfmin['vdiff'].mean() + dfmin['vdiff'].std()

            factor[stk] = dfmin[dfmin['vdiff'] > dfmin['vs']].std_next5.mean()
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T

        factor = abs(factor - factor.mean())        
        return factor
