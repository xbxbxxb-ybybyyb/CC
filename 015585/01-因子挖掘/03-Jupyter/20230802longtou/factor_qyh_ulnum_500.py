import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_ulnum_500'
# 0.03,17
def factor_qyh_ulnum_500(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -900)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close', 'pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['p_zt'] = df_ori['pre_close'].apply(lambda x: np.floor(x * 100 * 1.1 + 0.5) / 100)
    df_ori.loc[df_ori['zcz'] == 1,'p_zt'] = df_ori.loc[df_ori['zcz'] == 1,'pre_close'].apply(lambda x: np.floor(x * 100 * 1.2 + 0.5) / 100)
    df_ori['is_zt'] = (df_ori['close'] >= df_ori['p_zt'])
    # 过去n日涨停次数(包括当日)
    n = 500
    df_ori['ulnum_n'] = df_ori['is_zt'].unstack().rolling(n).sum().stack()
    f_data = pd.DataFrame(df_ori['ulnum_n'])
    f_data.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return f_data
