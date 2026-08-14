import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_amt5'
# 5日成交量均值
#
#
def factor_qyh_md_amt5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 100000000,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -5)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['amt','adjfactor'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori[factor_name] = df_ori['amt'].unstack().rolling(5,1).max().stack() * 1000
    df_ori[factor_name].replace(0,100000000,inplace = True)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
