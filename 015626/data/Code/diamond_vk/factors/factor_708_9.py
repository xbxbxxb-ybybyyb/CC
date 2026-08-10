from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 潮汐过程的价格的收益率
def get_timediff_minutes(start_time, end_time):
    m = (end_time - start_time).total_seconds() / 60
    if (start_time.hour <= 11) & (end_time.hour >= 13):
        return m - 90
    else:
        return m

class factor_708_9(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['volume', 'close', 'amount']
        super(factor_708_9, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        volume = df['volume'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        close = df['close'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        amount = df['amount'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in volume.columns.tolist():
            dfmin = pd.concat([volume[stk], close[stk], amount[stk]], axis = 1)
            dfmin.columns = ['volume', 'close', 'amount']
            if dfmin['amount'].sum() == 0:
                continue
            
            dfmin['v_neighbor'] = dfmin['volume'].rolling(9).sum().shift(-4)

            max_v_time = dfmin[4:].v_neighbor.argmax()
            up_time = dfmin.loc[:max_v_time].v_neighbor.argmin()
            down_time = dfmin.loc[max_v_time:].v_neighbor.argmin()
            
            all_time_num = get_timediff_minutes(up_time, down_time)
            up_time_num = get_timediff_minutes(up_time, max_v_time)
            down_time_num = get_timediff_minutes(max_v_time, down_time)

            tide_ret = dfmin.loc[down_time]['close'] / dfmin.loc[up_time]['close'] - 1
            tide_ret_mean = tide_ret / all_time_num * 1e5
            v_ud_ratio = dfmin.loc[up_time:max_v_time]['volume'].sum() / dfmin.loc[max_v_time:down_time]['volume'].sum()
            
            down_ret = dfmin.loc[down_time]['close'] / dfmin.loc[max_v_time]['close'] - 1
            up_ret = dfmin.loc[max_v_time]['close'] / dfmin.loc[up_time]['close'] - 1
            if down_ret == 0:
                r_ud_ratio = np.nan
            else:
                r_ud_ratio = up_ret / down_ret
                
            t_ud_ratio = up_time_num / all_time_num if all_time_num > 0 else np.nan
            
            if max_v_time == up_time:
                up_ratio = 0
            else:
                tide_ret_up = dfmin.loc[max_v_time]['close'] / dfmin.loc[up_time]['close'] - 1
                up_ratio = tide_ret_up / up_time_num * 1e5
                
            if max_v_time == down_time:
                down_ratio = 0
            else:
                tide_ret_down = dfmin.loc[down_time]['close'] / dfmin.loc[max_v_time]['close'] - 1
                down_ratio = tide_ret_down / down_time_num * 1e5
                
            # 强势半潮汐时段收益率的变动速率
            if dfmin.loc[up_time]['volume'] < dfmin.loc[down_time]['volume']:
                tide_ret1 = dfmin.loc[max_v_time]['close'] / dfmin.loc[up_time]['close'] - 1
                strong_ratio = tide_ret1 / up_time_num * 1e5 if up_time_num > 0 else np.nan
            else:
                tide_ret1 = dfmin.loc[down_time]['close'] / dfmin.loc[max_v_time]['close'] - 1
                strong_ratio = tide_ret1 / down_time_num * 1e5 if down_time_num > 0 else np.nan
            
            # 弱势半潮汐时段收益率的变动速率
            if dfmin.loc[up_time]['volume'] > dfmin.loc[down_time]['volume']:
                tide_ret2 = dfmin.loc[max_v_time]['close'] / dfmin.loc[up_time]['close'] - 1
                weak_ratio = tide_ret2 / up_time_num * 1e5 if up_time_num > 0 else np.nan
            else:
                tide_ret2 = dfmin.loc[down_time]['close'] / dfmin.loc[max_v_time]['close'] - 1
                weak_ratio = tide_ret2 / down_time_num * 1e5 if down_time_num > 0 else np.nan

            factor[stk] = [tide_ret, tide_ret_mean, v_ud_ratio, r_ud_ratio, t_ud_ratio, up_ratio, down_ratio, strong_ratio, weak_ratio]
        
        factor = pd.DataFrame(factor, index = ['factor_708','factor_709','factor_710','factor_711','factor_712','factor_713','factor_714','factor_715','factor_716']).T
        return factor