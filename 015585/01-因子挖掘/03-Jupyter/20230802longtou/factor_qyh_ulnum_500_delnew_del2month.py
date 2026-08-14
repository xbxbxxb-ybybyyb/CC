import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_ulnum_500_delnew_del2month'
# 0.03,17
def factor_qyh_ulnum_500_delnew_del2month(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -600)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close', 'pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['p_zt'] = df_ori['pre_close'].apply(lambda x: np.floor(x * 100 * 1.1 + 0.5) / 100)
    df_ori.loc[df_ori['zcz'] == 1,'p_zt'] = df_ori.loc[df_ori['zcz'] == 1,'pre_close'].apply(lambda x: np.floor(x * 100 * 1.2 + 0.5) / 100)
    df_ori['is_zt'] = (df_ori['close'] >= df_ori['p_zt'])
    # 用基本信息筛选，剔除上市3个月之内的涨停
    from xquant.thirdpartydata.factordata import FactorData
    FD = FactorData()
    df_info = FD.get_factor_value('WIND_AShareDescription', factors=['S_INFO_WINDCODE', 'S_INFO_LISTDATE'])
    df_ori = pd.merge(df_ori.reset_index(), df_info, left_on='Ticker', right_on='S_INFO_WINDCODE')
    df_ori['S_INFO_LISTDATE'] = df_ori['S_INFO_LISTDATE'].apply(lambda x : pd.Timestamp(str(x)))
    df_ori['is_1mon'] = 1
    df_ori.loc[df_ori['dt'] < df_ori['S_INFO_LISTDATE'] + pd.Timedelta(days = 90),'is_1mon'] = 0
    df_ori = df_ori[df_ori['is_1mon'] == 1].set_index(['dt','Ticker'])
    # 过去n日涨停次数(包括当日)
    n = 500
    df_ori['ulnum_n'] = df_ori['is_zt'].unstack().rolling(n).sum().stack()
    # 减去过去6个月的
    df_ori['ulnum_n'] = df_ori['ulnum_n'] - df_ori['is_zt'].unstack().rolling(22*6).sum().stack()
    f_data = pd.DataFrame(df_ori['ulnum_n'])
    f_data.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return f_data
