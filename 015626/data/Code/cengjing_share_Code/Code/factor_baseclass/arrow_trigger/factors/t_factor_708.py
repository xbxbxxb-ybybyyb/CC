from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 潮汐过程的价格的收益率
class t_factor_708(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction']
        super(t_factor_708, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[data.TradeType == 0].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':'last', 'TradeQty':'sum', 'TradeMoney':'sum'})
            dfmin.columns =  ['close', 'volume', 'amount']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['close'])

            dfmin['v_neighbor'] = dfmin['volume'].rolling(9).sum().shift(-4)

            max_v_time = dfmin.v_neighbor.argmax()
            up_time = dfmin.loc[:max_v_time].v_neighbor.argmin()
            down_time = dfmin.loc[max_v_time:].v_neighbor.argmin()

            tide_ret = dfmin.loc[down_time]['close'] / dfmin.loc[up_time]['close'] - 1

            factor[stk] = tide_ret
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T

        return factor