# dtj
# 5min股价vwap在open和close之间的比例,5日均值
# 0.055,15
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_vwap2oc_5'
def factor_qyh_m5_vwap2oc_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.54, 'data': ['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    open_data = IO.read_data([start_date, end_date]
                             , alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    close_data = IO.read_data([start_date, end_date]
                            , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    amt_data = IO.read_data([start_date, end_date]
                            , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    volume_data = IO.read_data([start_date, end_date]
                            , alt='/data/group/800463/data/generalStrong/minute5/volume.h5')
    vwap_data = amt_data / volume_data
    vwap_data = vwap_data.fillna(0)
    open_data = open_data.fillna(0)
    close_data = close_data.fillna(0)
    res = (vwap_data - open_data)*(vwap_data - close_data) < 0
    res = res.mean(axis=1)
    res = pd.DataFrame(res.unstack().rolling(5, 2).mean().stack())
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res