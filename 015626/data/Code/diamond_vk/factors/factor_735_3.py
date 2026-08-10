from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

# 跟随系数 方正11
def get_timediff_minutes(start_time, end_time):
    m = (end_time - start_time).total_seconds() / 60
    if (start_time.hour <= 11) & (end_time.hour >= 13):
        return m - 90
    else:
        return m

class factor_735_3(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['close', 'volume']
        super(factor_735_3, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        close = df['close'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        volume = df['volume'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in volume.columns.tolist():
            dfmin = pd.concat([close[stk], volume[stk]], axis = 1)
            dfmin.columns = ['close', 'volume']
            if dfmin['volume'].sum() == 0:
                continue
                
            dfmin = dfmin.between_time('945', '1456')
            stime_list = dfmin.index.tolist()
            t_list = sorted(dfmin.sort_values(by = 'volume', ascending = False).head(10).index.tolist())
            sea_list = [t_list[0]]
            t_index = stime_list.index(t_list[0])
            v_list = [[dfmin.loc[t_list[0]]['volume'], dfmin.loc[stime_list[t_index+1:t_index+6]]['volume'].sum()]]
            for i in range(1, len(t_list)):
                if get_timediff_minutes(sea_list[-1], t_list[i]) > 5:
                    sea_list.append(t_list[i])
                    t_index = stime_list.index(t_list[i])
                    v_list.append([dfmin.loc[t_list[i]]['volume'], dfmin.loc[stime_list[t_index+1:t_index+6]]['volume'].sum()])
            vdf = pd.DataFrame(v_list, columns = ['sea', 'follow'], index = sea_list)

            follow_sea = (vdf['follow'] / vdf['sea']).mean()
            sea_ratio = vdf['sea'].sum() / dfmin['volume'].sum()
            follow_ratio = vdf['follow'].sum() / dfmin['volume'].sum() 
            
            factor[stk] = [follow_sea, sea_ratio, follow_ratio]

        factor = pd.DataFrame(factor, index = ['factor_735_0', 'factor_735_1', 'factor_735_2']).T
        
        return factor
    