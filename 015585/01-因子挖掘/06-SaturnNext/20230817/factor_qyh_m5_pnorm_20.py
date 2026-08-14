#
# 5min股价对应振幅小于2%的次数占比,20日均值
# 0.057，17（5）
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_pnorm_20'
def factor_qyh_m5_pnorm_20(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.15,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    high_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/high.h5')
    low_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/low.h5')
    amp_data = high_data / low_data - 1
    amp_data = abs(amp_data)>=0.02
    res = 1-amp_data.mean(axis=1)
    res = pd.DataFrame(res.unstack().rolling(3,2).mean().stack())
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res