import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_pct20_time'
# 20日动量，根据距离最新的时间线性加权
# -0.05,24;强势股：-0.03
#
def factor_qyh_md_pct20_time(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -5)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori = df_ori['pct_chg'].unstack()
    res = pd.DataFrame()
    for i in range(20):
        if i == 0:
            res = df_ori * (20-i)
        else:
            res += df_ori.shift(i) * (20-i)
    res = pd.DataFrame((res/(21*20/2)).stack())
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res[[factor_name]]
