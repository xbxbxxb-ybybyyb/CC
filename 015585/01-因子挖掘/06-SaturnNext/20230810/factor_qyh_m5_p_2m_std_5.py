# dtj
# 股价当日波动率/全市场平均波动率，5日平均
# 14,-0.04
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_p_2m_std_5'
def factor_qyh_m5_p_2m_std_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.4,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    close_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    close_data['cv'] = close_data.std(axis=1) / close_data.mean(axis=1)
    res = pd.DataFrame(close_data['cv'] / close_data['cv'].groupby('dt').mean())
    #
    res.columns = [factor_name]
    res = res.unstack().rolling(5,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return res