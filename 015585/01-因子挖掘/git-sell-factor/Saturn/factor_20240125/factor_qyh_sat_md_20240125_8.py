import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_sat_md_20240125_8'
def factor_qyh_sat_md_20240125_8(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    import decimal
    def round_(x, n=0):
        x = x + 1e-8
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['vwap','pre_close','adjfactor','close','high','low','amt','pct_chg','turn'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori = df_ori[(df_ori['amt'] > 0) & (df_ori['vwap'] > 0) & df_ori['close'] > 0]
    x = 'vwap'
    y = 'close'
    df_ori['xy'] = (df_ori[x] * df_ori[y])
    df_ori['exy'] = df_ori['xy'].unstack().rolling(20,5).mean().stack()
    df_ori['ex'] = df_ori[x].unstack().rolling(20,5).mean().stack()
    df_ori['ey'] = df_ori[y].unstack().rolling(20,5).mean().stack()
    df_ori['stdx'] = df_ori[x].unstack().rolling(20,5).std().stack()
    df_ori['stdy'] = df_ori[y].unstack().rolling(20,5).std().stack()
    df_ori['factor'] = ((df_ori['exy'] - df_ori['ex'] * df_ori['ey'])
                        /(df_ori['stdx'] * df_ori['stdy'] + 1e-4).apply(lambda x : round_(x,6)))
    df_ori['factor'] = df_ori['factor'].apply(lambda x: 1 if x > 1.0001 else -1 if x < -1.0001 else x)
    df_ori['med'] = df_ori['factor'].unstack().rolling(5,1).median().stack()
    df_ori = df_ori[abs(df_ori['med']) > 1e-6]
    df_ori[factor_name] = (df_ori['factor']) / df_ori['med']
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x :round_(x,3))
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]