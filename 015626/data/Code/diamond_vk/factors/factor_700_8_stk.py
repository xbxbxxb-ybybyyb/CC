from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 日耀眼波动率
class factor_700_8_stk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['volume_stk', 'close_stk', 'amount_stk']
        super(factor_700_8_stk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close_stk'].index.date[-1]
        volume = df['volume_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        close = df['close_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        amount = df['amount_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in volume.columns.tolist():
            dfmin = pd.concat([volume[stk], close[stk], amount[stk]], axis = 1)
            dfmin.columns = ['volume', 'close', 'amount']
            if dfmin['amount'].sum() == 0:
                continue
            
            dfmin['ret'] = dfmin.close.pct_change()
            dfmin['std_next5'] = dfmin['ret'].rolling(5).std().shift(-4)

            dfmin['vdiff'] = dfmin.volume.diff()
            dfmin['vs'] = dfmin['vdiff'].mean() + dfmin['vdiff'].std()
            
            temp = dfmin[dfmin['vdiff'] > dfmin['vs']]
            std_mean = temp.std_next5.mean()
            ret_mean = temp.ret.mean()
            amount_ratio = temp.amount.sum() / dfmin.amount.sum()
            ret_amount = 1e10 * temp.ret.sum() / temp.amount.sum()
            ret_num = len(temp[temp['ret'] > 0.005])
            temp_num = len(temp)
            factor[stk] = [std_mean, ret_mean, amount_ratio, ret_amount, ret_num, temp_num]
        
        factor = pd.DataFrame(factor, index = ['factor_700','factor_702', 'factor_704', 'factor_705', 'factor_706', 'factor_707']).T
        factor['factor_700_amm'] = abs(factor['factor_700'] - factor['factor_700'].mean())
        factor['factor_702_amm'] = abs(factor['factor_702'] - factor['factor_702'].mean())
        return factor.add_suffix('_stk')