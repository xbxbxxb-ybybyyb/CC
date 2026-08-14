#
# 前日股价波动率/5日平均波动率
# 12,-0.035
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_p_std_5'
def factor_qyh_m5_p_std_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    close_data['std'] = close_data.std(axis = 1)
    res = close_data['std'] / close_data['std'].unstack().rolling(5,3).mean().stack()
    res = pd.DataFrame(res,columns=[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return res