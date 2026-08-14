import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_f5ratio_10_min'
def factor_qyh_m5_f5ratio_10_min(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 11,'data':['minute5','MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['amt']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    qty_data = IO.read_data([start_date, end_date]
                          , alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    f_data[factor_name] = ((qty_data['m925'] + qty_data['m930']) / f_data['amt']).unstack()\
        .rolling(10,1).min().stack()
    res = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return res