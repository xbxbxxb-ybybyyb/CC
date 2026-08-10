from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 集合竞价tick因子
class factor_801_24(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick']
        super(factor_801_24, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            tick = df['tick'][stk]
            pre_close = tick.iloc[-1]['PreClosePx'] 
            limit_px = tick.iloc[-1]['MaxPx']
            stop_px = tick.iloc[-1]['MinPx']
            tick['ret'] = tick['Buy1Price'] / pre_close - 1
            tick['Buy1Price_diff'] = tick['Buy1Price'].diff()
            tick_last1min = tick[(tick['dt'].dt.time >= datetime.time(9, 24)) & (tick['Buy1Price'] == tick['Sell1Price'])]
            tick2 = tick[(tick['dt'].dt.time >= datetime.time(9, 20, 3)) & (tick['Buy1Price'] == tick['Sell1Price'])]
            tick1 = tick[(tick['dt'].dt.time < datetime.time(9, 20, 3)) & (tick['Buy1Price'] == tick['Sell1Price'])]
            if len(tick) == 0 or len(tick_last1min) == 0 or len(tick2) == 0 or len(tick1) == 0:
                continue
               
            f1list = [tick1['ret'].max(), tick1['ret'].min(), tick1['ret'].mean(), tick1['ret'].median(), tick1['ret'].std(), tick1['ret'].skew(), tick1['ret'].kurt()]
            f2list = [tick2['ret'].max(), tick2['ret'].min(), tick2['ret'].mean(), tick2['ret'].median(), tick2['ret'].std(), tick2['ret'].skew(), tick2['ret'].kurt()]
            is1limit = int(tick1['Buy1Price'].max() == limit_px)
            is1stop = int(tick1['Buy1Price'].min() == stop_px)
            is2limit = int(tick2['Buy1Price'].max() == limit_px)
            is2stop = int(tick2['Buy1Price'].min() == stop_px)
            limit_ret1 = tick1['Buy1Price'].max() / limit_px - 1
            stop_ret1 = tick1['Buy1Price'].min() / stop_px - 1
            limit_ret2 = tick2['Buy1Price'].max() / limit_px - 1
            stop_ret2 = tick2['Buy1Price'].min() / stop_px - 1
            up_ratio1 = len(tick1[tick1['Buy1Price_diff'] >= 0]) / len(tick1)
            up_ratio2 = len(tick2[tick2['Buy1Price_diff'] >= 0]) / len(tick2)

            factor[stk] = [is1limit, is1stop, is2limit, is2stop, limit_ret1, stop_ret1, limit_ret2, stop_ret2, up_ratio1, up_ratio2] + f1list + f2list

        factor = pd.DataFrame(factor, index = [f'factor_801_{i}' for i in range(24)]).T

        return factor