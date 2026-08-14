
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_up2dn_c2o_5'
def factor_qyh_m5_up2dn_c2o_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    open_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    delta_data = close_data-open_data
    delta_data['red'] = delta_data[delta_data > 0].mean(axis=1) / close_data.mean(axis=1)
    delta_data['green'] = delta_data[delta_data < 0].mean(axis=1) / close_data.mean(axis=1)
    delta_data[factor_name] = (delta_data['red'] - (-delta_data['green']))\
        .unstack().rolling(5,1).mean().stack()
    res = pd.DataFrame(delta_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return res