
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_p_std_20_new'
def factor_qyh_m5_p_std_20_new(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                              , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    close_data['std'] = close_data.std(axis=1)
    close_data['std'] = close_data['std'].apply(lambda x: 0 if abs(x) < 0.0000001 else x)
    close_data['std20'] = close_data['std'].unstack().rolling(20, 5).mean().stack()
    close_data['std20'] = close_data['std20'].apply(lambda x: np.nan if abs(x) < 0.0000001 else x)
    close_data[factor_name] = close_data['std'] / close_data['std20']
    res = pd.DataFrame(close_data[factor_name], columns=[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return res