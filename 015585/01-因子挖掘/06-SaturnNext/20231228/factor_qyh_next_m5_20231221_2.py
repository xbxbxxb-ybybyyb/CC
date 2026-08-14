import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()

# dtj,zcz
# 过去5日，vwap-挂买的均值
#
factor_name = 'qyh_next_m5_20231221_2'
def factor_qyh_next_m5_20231221_2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    df_close = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/minute5/close.h5')
    df_high = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/minute5/high.h5')
    df_low = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/minute5/low.h5')
    df_delta = df_close.sub(0.5*(df_high+df_low))
    res = df_delta.div(df_close)
    res = pd.DataFrame(res.mean(axis=1))
    res.columns = [factor_name]
    res['zcz'] = (((res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                res.reset_index()['dt'] >= '2020-08-24'))
                 | (res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    res.loc[res['zcz']==1,factor_name] = res.loc[res['zcz']==1,factor_name]/2
    res[factor_name] = res[factor_name].unstack().rolling(10,1).median().stack()
    res[factor_name] = res[factor_name] * 100
    # -------------------------------------------------------------------------------------------------------------------
    return res[[factor_name]]
