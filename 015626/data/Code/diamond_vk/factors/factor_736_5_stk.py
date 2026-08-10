from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 开源3 聪明钱因子
class factor_736_5_stk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['close_stk', 'volume_stk', 'amount_stk']
        super(factor_736_5_stk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close_stk'].index.date[-1]
        close = df['close_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        volume = df['volume_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        amount = df['amount_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in volume.columns.tolist():
            dfmin = pd.concat([close[stk], volume[stk], amount[stk]], axis = 1)
            dfmin.columns = ['close', 'volume', 'amount']
            if dfmin['volume'].sum() == 0:
                continue
                
            dfmin['ret'] = dfmin['close'].pct_change()
            dfmin['s1'] = abs(dfmin['ret']) / (dfmin['volume'] ** 0.5)
            dfmin['s2'] = abs(dfmin['ret']) / (dfmin['volume'] ** 0.1)
            dfmin['s3'] = abs(dfmin['ret']).rank() + dfmin['volume'].rank()
            dfmin['s4'] = abs(dfmin['ret']) / dfmin['volume'].replace(0, np.nan).apply(lambda x:math.log(x, 10))
            dfmin['s5'] = dfmin['volume']

            vwap = dfmin['amount'].sum() / dfmin['volume'].sum()
            volume_t = dfmin['volume'].sum() * 0.2

            f_list = []
            for k in ['s1','s2','s3','s4', 's5']:
                temp = dfmin.sort_values(by = k, ascending = False)
                temp['volume_cs'] = temp['volume'].cumsum().shift(1).fillna(method = 'bfill')
                temp = temp[temp['volume_cs'] <= volume_t]
                f_list.append((temp['amount'].sum() / temp['volume'].sum() / vwap - 1) * 1000)

            factor[stk] = f_list

        factor = pd.DataFrame(factor, index = ['factor_736_0', 'factor_736_1', 'factor_736_2', 'factor_736_3', 'factor_736_4']).T

        return factor.add_suffix('_stk')