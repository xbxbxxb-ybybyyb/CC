# dtj
# 上涨时的成交额/总成交额，回溯5日
# -0.07,32
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_vol_up_5'
def factor_qyh_m5_vol_up_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.57,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    open_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    amt_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    amt_data_filter = amt_data * (close_data >= open_data)
    res = amt_data_filter.sum(axis=1) / amt_data.sum(axis=1)
    res = pd.DataFrame(res,columns=[factor_name]).unstack().rolling(5,2).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return res