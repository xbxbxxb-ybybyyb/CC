from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd
# 孤雁出群
class factor_733_stk(FactorGenerator):
    def __init__(self, *args, **kwargs):
        required_columns = ['close_stk', 'volume_stk', 'amount_stk']
        super(factor_733_stk, self).__init__(*args, required_columns=required_columns, **kwargs)

    def on_bar(self, df):
        tday = df['close_stk'].index.date[-1]
        close = df['close_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)
        amount = df['amount_stk'].loc[tday.strftime('%Y%m%d')].between_time(data_morning_begin, data_afternoon_end)

        amount_list = []
        retdf_list = []
        for stk in amount.columns.tolist():
            _ = close[stk]
            _ = amount[stk]
            dfmin = pd.concat([close[stk], amount[stk]], axis = 1)
            dfmin.columns = ['close', 'amount']
            if dfmin['amount'].sum() == 0:
                continue

            amount2 = dfmin[['amount']]
            amount2.columns = [stk]
            amount_list.append(amount2)
            
            dfmin['ret'] = dfmin['close'].pct_change()
            retdf_list.append(dfmin['ret'])

        retdf = pd.concat(retdf_list, axis = 1)
        ret_std = retdf.std(axis = 1)
        low_ret_std = ret_std[ret_std < ret_std.mean()]

        amount_all = pd.concat(amount_list, axis = 1).reindex(low_ret_std.index)

        if len(amount_all) > 1:
            factor = ((amount_all.corr(method = 'pearson').abs().sum(axis = 1) - 1) / (len(amount_all) - 1)).to_frame()
            factor.columns = [self.__class__.__name__]
        else:
            factor = pd.DataFrame([np.nan] * len(df['universe']), index = df['universe'], columns = [self.__class__.__name__])
        
        return factor