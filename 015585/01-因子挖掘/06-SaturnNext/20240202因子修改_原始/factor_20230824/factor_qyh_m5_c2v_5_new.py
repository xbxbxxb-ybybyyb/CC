# dtj
# 5min股价close/vwap均值，回溯5日
# -0.03,17
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_c2v_5_new'
def factor_qyh_m5_c2v_5_new(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.2, 'data': ['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                            , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    amt_data = IO.read_data([start_date, end_date]
                            , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    volume_data = IO.read_data([start_date, end_date]
                            , alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    vwap_data = amt_data / volume_data

    res = (close_data / vwap_data - 1).mean(axis = 1)
    res = pd.DataFrame(res.unstack().rolling(5, 2).mean().stack())
    res = res * 1000
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res