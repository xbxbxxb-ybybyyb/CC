#
# 当日5分钟振幅在全市场排名，追溯20日均值
# gg
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_amp_rank_20'
def factor_qyh_m5_amp_rank_20(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    high_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/high.h5')
    low_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/low.h5')
    amp_data = high_data / low_data - 1
    amp_data[factor_name] = amp_data.mean(axis=1)
    res = amp_data[factor_name].groupby('dt').rank() / amp_data[factor_name].groupby('dt').count()
    #
    res = pd.DataFrame(res,columns = [factor_name]).unstack().rolling(20,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return res