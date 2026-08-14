import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_pct20'
# 20日动量：
#
#
def factor_qyh_md_pct20(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -5)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori[factor_name] = df_ori['pct_chg'].unstack().rolling(20,5).mean().stack()
    # df_ori[factor_name] = df_ori['3']
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
