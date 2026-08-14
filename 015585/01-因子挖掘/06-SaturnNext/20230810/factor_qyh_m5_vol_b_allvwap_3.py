#
# 5min价格在全局vwap上的成交量占比
#
# gg
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_vol_b_allvwap_3'
def factor_qyh_m5_vol_b_allvwap_3(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    open_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    amt_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    volume_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    allvwap_data = amt_data.cumsum(axis = 1) / volume_data.cumsum(axis = 1)
    volume_data_filter = volume_data * (close_data > allvwap_data) * (open_data > allvwap_data)
    res = volume_data_filter.sum(axis = 1) / volume_data.sum(axis=1)
    res = pd.DataFrame(res,columns=[factor_name]).unstack().rolling(3,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return res