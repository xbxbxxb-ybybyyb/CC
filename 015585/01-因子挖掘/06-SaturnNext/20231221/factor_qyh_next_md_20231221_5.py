import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj,zcz
# 涨跌幅9日中位数
# 33，-0.072，-0.062
# skk_20231130_5：25
factor_name = 'qyh_next_md_20231221_5'
def factor_qyh_next_md_20231221_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0.75,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    start_date = int(s.tradingday(str(start_date), -180)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['high','low','adjfactor','amt','pct_chg','vwap','close','pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    #
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['para'] = (df_ori['high'] - df_ori['low']).unstack().rolling(20,1).max().stack()
    df_ori = df_ori[df_ori['para']>1e-5]
    df_ori = df_ori[df_ori['amt']>1e-5]
    df_ori.loc[df_ori['zcz']==1,'pct_chg'] = df_ori.loc[df_ori['zcz']==1,'pct_chg']/2
    df_ori[factor_name] = df_ori['pct_chg'].unstack().rolling(9,1).median().stack()
    #
    df_ori.loc[df_ori[factor_name] > 6,factor_name] = 12 - df_ori.loc[df_ori[factor_name] > 6,factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]