#
# 5分钟成交量/abs(涨跌幅)
# gg
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_amt2pct_5'
def factor_qyh_m5_amt2pct_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.74,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    open_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/open.h5')
    amt_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    pct_data = close_data / open_data - 1
    res = (abs(pct_data)/np.log(amt_data+1)).mean(axis=1)
    #
    res = pd.DataFrame(res,columns = [factor_name]).unstack().rolling(5,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return res