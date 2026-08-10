
from arrow.factor_generator import FactorGenerator
from arrow.naming_config import *
from arrow.utility import *
import datetime, math
import numpy as np
import bottleneck as bk
import pandas as pd
# 集合竞价tick因子
class factor_800_16(FactorGenerator):
    def __init__(self, *args, **kwargs):
        data_mode = 't'
        required_columns = ['tick']
        super(factor_800_16, self).__init__(*args, data_mode = data_mode, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        factor = {}
        for stk in df['universe']:
            tick = df['tick'][stk]
            tick['Buy1Price_diff'] = tick['Buy1Price'].diff()
            tick_last1min = tick[(tick['dt'].dt.time >= datetime.time(9, 24)) & (tick['Buy1Price'] == tick['Sell1Price'])]
            tick_last5min = tick[(tick['dt'].dt.time >= datetime.time(9, 20, 3)) & (tick['Buy1Price'] == tick['Sell1Price'])]
            tick1 = tick[(tick['dt'].dt.time < datetime.time(9, 20, 3)) & (tick['Buy1Price'] == tick['Sell1Price'])]
            if len(tick) == 0 or len(tick_last1min) == 0 or len(tick_last5min) == 0 or len(tick1) == 0:
                continue
               
            pre_close = tick.iloc[-1]['PreClosePx'] 
            px924 = tick_last1min.iloc[0]['Buy1Price']
            volume924 = tick_last1min.iloc[0]['Buy1OrderQty']
            px925 = tick.iloc[-1]['LastPx']
            volume925 = tick.iloc[-1]['TotalVolumeTrade']
            px920 = tick_last5min.iloc[0]['Buy1Price']
            volume920 = tick_last5min.iloc[0]['Buy1OrderQty']

            p_ratio1 = px925 / px924 - 1
            v_ratio1 = volume925 / volume924 - 1
            pv_ratio1 = p_ratio1 / (volume925 - volume924)

            p_ratio2 = px924 / px920 - 1
            v_ratio2 = volume924 / volume920 - 1
            pv_ratio2 = p_ratio2 / (volume924 - volume920)
            pv_ratio12 = pv_ratio1 / pv_ratio2 - 1

            p_ratios = p_ratio2 + 2*p_ratio1
            p_ratio = px925 / px920 - 1

            v_down_ratio = tick1.iloc[-1]['Buy1OrderQty'] / tick1['Buy1OrderQty'].max() - 1
            p_down_ratio = tick1.iloc[-1]['Buy1Price'] / tick1.loc[tick1['Buy1OrderQty'].idxmax()]['Buy1Price'] - 1

            p_path = (px925-px920) / tick_last5min['Buy1Price_diff'].abs().sum()
            vv_ratio = (volume925 - volume924) / ((volume924 - volume920) / 4) * np.sign(p_ratio1)

            ratio_1 = tick1.iloc[0]['Buy1Price'] / pre_close - 1
            ratio_2 = tick1.iloc[-1]['Buy1Price'] / pre_close - 1
            ratio_3 = tick1.iloc[-1]['Buy1Price'] / tick1.iloc[0]['Buy1Price'] - 1

            factor[stk] = [p_ratio1, v_ratio1, pv_ratio1, p_ratio2, v_ratio2, pv_ratio2, pv_ratio12, p_ratios, p_ratio, 
                           v_down_ratio, p_down_ratio, p_path, vv_ratio, ratio_1, ratio_2, ratio_3]

        factor = pd.DataFrame(factor, index = [f'factor_800_{i}' for i in range(16)]).T

        return factor