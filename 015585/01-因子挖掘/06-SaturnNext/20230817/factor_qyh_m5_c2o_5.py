#
# 5分钟上涨和下跌的幅度比，5日均值
#
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_c2o_5'
def factor_qyh_m5_c2o_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.15,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    open_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    delta_data = close_data-open_data
    delta_data['red'] = delta_data[delta_data > 0].sum
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res