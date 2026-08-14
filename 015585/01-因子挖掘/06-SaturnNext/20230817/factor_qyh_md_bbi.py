# bbi:3,6,12,24
# 0.07,30
# qyh_md_ma_10:31
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_bbi'
def factor_qyh_md_bbi(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.78,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['vwap']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    coef = [3,6,12,24]

    for i in coef:
        f_data['ma' + str(i)] = f_data['vwap'].unstack().rolling(i,1).mean().stack()
    f_data['bbi'] = 0
    for i in coef:
        f_data['bbi'] = f_data['bbi'] + f_data['ma' + str(i)] * (i - sum(coef)) / sum(coef)
    res = f_data['vwap'] / f_data['bbi'] - 1
    res = pd.DataFrame(res)
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res