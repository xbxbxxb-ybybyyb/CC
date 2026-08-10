from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 潮汐过程的价格的收益率的变动速率
def get_timediff_minutes(start_time, end_time):
    m = (end_time - start_time).total_seconds() / 60
    if (start_time.hour <= 11) & (end_time.hour >= 13):
        return m - 90
    else:
        return m

class factor_712(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction']
        super(factor_712, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

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


            factor[stk] = get_timediff_minutes(up_time, max_v_time) / get_timediff_minutes(up_time, down_time)
            
        factor = pd.DataFrame(factor, index = [self.__class__.__name__]).T

        return factor