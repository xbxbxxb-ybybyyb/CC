from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 模糊性
class factor_726_5(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['close', 'amount', 'volume']
        super(factor_726_5, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close'].index.date[-1]
        close = df['close'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        volume = df['volume'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        amount = df['amount'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        
        factor = {}
        for stk in close.columns.tolist():
            dfmin = pd.concat([close[stk], amount[stk], volume[stk]], axis = 1)
            dfmin.columns = ['close', 'amount', 'volume']
            if dfmin['amount'].sum() == 0:
                continue
            
            dfmin['ret'] = dfmin['close'].pct_change()
            dfmin['vol'] = dfmin['ret'].rolling(5, min_periods = 5).std()
            dfmin['vol_vol'] = dfmin['vol'].rolling(5, min_periods = 5).std()

            vol_vol = dfmin['vol_vol'].mean() * 1e5
            # 下午模糊性与上午模糊性之比
            temp = dfmin.between_time(data_morning_begin, data_morning_end)['vol_vol'].mean()
            vv_an = dfmin.between_time(data_afternoon_begin, data_afternoon_end)['vol_vol'].mean() / temp - 1 if temp != 0 else np.nan
            # 模糊关联度因子
            vva_corr = dfmin['vol_vol'].corr(dfmin['amount'])
            # 模糊金额比
            vm = dfmin['vol_vol'].mean()
            ar = dfmin[dfmin['vol_vol'] > vm]['amount'].mean() / dfmin['amount'].mean()
            vr = dfmin[dfmin['vol_vol'] > vm]['volume'].mean() / dfmin['volume'].mean()
            # 模糊金额比 / 模糊数量比 - 1
            ar_vr = ar / vr - 1 if vr != 0 else np.nan
            
            factor[stk] = [vol_vol, vv_an, vva_corr, ar, ar_vr]
                                    
        factor = pd.DataFrame(factor, index = [f'factor_{i}' for i in range(726, 731)]).T
        return factor