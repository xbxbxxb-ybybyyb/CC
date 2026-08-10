from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
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

class t_factor_735_3(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['transaction']
        super(t_factor_735_3, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            data = df['transaction'][stk]
            data = data[data.TradeType == 0].set_index('dt')

            dfmin = data.resample('1min').agg({'TradePrice':['first','last'], 'TradeQty':'sum'})
            dfmin.columns =  ['open', 'close', 'volume']
            dfmin = dfmin.between_time('930', '1456').dropna(subset = ['open'])
            dfmin[['open', 'close']] = dfmin[['open', 'close']].fillna(method = 'ffill')

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
        
        return factor.add_prefix('t_')