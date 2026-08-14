import numpy as np
import pandas as pd
import decimal
from functions import *
from xquant.factordata import FactorData
s = FactorData()

factor_name = 'h2v_amtstd_nofilter_240_std_amtdiv'#
def factor_h2v_amtstd_nofilter_240_std_amtdiv(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0}
    factor_explain = "h2v_amtstd_nofilter_240_std_amtdiv"
    start_date = int(s.tradingday(str(start_date), -300)[0])
    df_ori = IO.read_data([start_date, end_date],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
            df_ori.reset_index()['dt'] >= '2020-08-24'))
                     | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori['bj'] = (df_ori.reset_index()['Ticker'].apply(lambda x: x[-2:] == 'BJ')).values
    for col in ['high', 'low', 'open', 'vwap', 'close']:
        if col in df_ori.columns:
            df_ori.loc[df_ori['zcz'] == 1, col] = ((df_ori.loc[df_ori['zcz'] == 1, col] - 1) / 2 + 1) * \
                                                  df_ori.loc[df_ori['zcz'] == 1, 'pre_close']
            df_ori.loc[df_ori['bj'] == 1, col] = ((df_ori.loc[df_ori['bj'] == 1, col] - 1) / 3 + 1) * \
                                                 df_ori.loc[df_ori['bj'] == 1, 'pre_close']
    for col in ['high', 'low', 'open', 'vwap', 'close', 'pre_close']:
        df_ori[col] = df_ori[col] * df_ori['adjfactor']

    df_ori['factor'] = df_ori['high'] / df_ori['vwap']
    df_ori['factor'] = df_ori['factor'] * df_ori['amt']
    df_ori[factor_name] = df_ori['factor'].unstack().rolling(240,1).apply(lambda x : f_calc_std(x)).stack()
    df_ori["amt"] = df_ori['amt'].unstack().rolling(240,1).apply(lambda x : f_calc_std(x)).stack()
    df_ori[factor_name] = df_ori[factor_name] / df_ori['amt'].replace(0,np.nan)
    
    return df_ori[[factor_name]]