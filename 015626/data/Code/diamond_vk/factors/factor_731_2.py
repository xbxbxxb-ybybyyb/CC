from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 日跳跃度因子
class factor_731_2(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['high', 'low', 'close', 'amount']
        super(factor_731_2, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        high = df['high'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        low = df['low'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        close = df['close'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        amount = df['amount'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in close.columns.tolist():
            dfmin = pd.concat([high[stk], low[stk], close[stk], amount[stk]], axis = 1)
            dfmin.columns = ['high', 'low', 'close', 'amount']
            if dfmin['amount'].sum() == 0:
                continue
            amplitude = dfmin['high'].max() / dfmin['low'].min() - 1
            
            dfmin['ret1'] = dfmin['close'].pct_change()
            dfmin['ret2'] = np.log(dfmin['close'] / dfmin['close'].shift())
            dfmin['ret_diff'] = dfmin['ret1'] - dfmin['ret2']
            dfmin['res'] = dfmin['ret_diff'] * 2 - dfmin['ret2'] ** 2
            # 日跳跃度因子
            f1 = dfmin['res'].mean() * 1e8
            
            factor[stk] = [f1, amplitude]
        # 日跳跃度以及振幅调整                   
        factor = pd.DataFrame(factor, index = ['factor_731', 'factor_732']).T
        factor.loc[factor['factor_731'] < factor['factor_731'].mean(), 'factor_732'] = factor['factor_732'] * -1
        return factor