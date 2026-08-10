from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 尾盘3分钟
class factor_805_8(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't-1'
        required_columns = ['transaction', 'tick']
        super(factor_805_8, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            tick = df['tick'][stk]
            tran = df['transaction'][stk]
            tran = tran[(tran.TradeType == 0) & (tran.TradePrice > 0)]

            tran1 = tran[tran['dt'].dt.time >= datetime.time(14, 57)]
            tran2 = tran[tran['dt'].dt.time <= datetime.time(14, 56)]

            tick['Buy1Price_diff'] = tick['Buy1Price'].diff()
            tick1 = tick[(tick['dt'].dt.time >= datetime.time(14, 57)) & (tick['Buy1Price'] == tick['Sell1Price']) & (tick['Buy1Price'] != 0)]
            if len(tick1) == 0 or len(tran1) == 0:
                continue

            close1456 = tran2.iloc[-1]['TradePrice']
            close = tran1.iloc[-1]['TradePrice']

            tick1['tick_ret'] = tick1['Buy1Price'] / close1456
            ret1 = close / tick1['Buy1Price'].max() - 1
            ret2 = close / tick1['Buy1Price'].min() - 1
            up_ratio = len(tick1[tick1['Buy1Price_diff'] >= 0]) / len(tick1)
            down_ratio = len(tick1[tick1['Buy1Price_diff'] <= 0]) / len(tick1)
            abspath_ratio = tick1['Buy1Price_diff'].abs().sum() / (close - close1456)
            flist = [tick1['tick_ret'].max(),tick1['tick_ret'].min(),tick1['tick_ret'].mean(), ret1, ret2, up_ratio, down_ratio, abspath_ratio]

            factor[stk] = flist         

        factor = pd.DataFrame(factor, index = [f'factor_805_{i}' for i in range(8)]).T

        return factor