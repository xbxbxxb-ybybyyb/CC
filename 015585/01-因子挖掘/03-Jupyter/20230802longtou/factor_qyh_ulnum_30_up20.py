import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_ulnum_30_up20'
def factor_qyh_ulnum_30_up20(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
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
    n = 30
    # df_ori['ulnum_n'] = df_ori['is_zt'].unstack().rolling(n).sum().stack()
    # 连板数
    def get_ctn_num(x,n):
        if len(x[x == False]) == 0:
            return n
        else:
            return n-1 - [j for j, k in enumerate(x) if k == False][-1]
    df_ori['ctn_num'] = df_ori['is_zt'].unstack().rolling(n).apply(lambda x: get_ctn_num(x,n)).stack()
    df_ori['ctn_num_calc'] = df_ori['ctn_num'].apply(lambda x: 0 if x > 2 else 1 if x == 2 else x)
    ## 2连板以上的只记为2
    df_ori['cnt_num_n_transfer'] = df_ori['ctn_num_calc'].unstack().rolling(n).sum().stack()
    # 必须高于20日线
    df_ori['ma20'] = df_ori['close'].unstack().rolling(20,5).mean().stack()
    df_ori.loc[df_ori['close'] < df_ori['ma20'],'cnt_num_n_transfer'] = 0
    f_data = pd.DataFrame(df_ori['cnt_num_n_transfer'])
    f_data.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return f_data
