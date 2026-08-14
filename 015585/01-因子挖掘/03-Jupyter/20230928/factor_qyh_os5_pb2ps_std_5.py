import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_os5_pb2ps_std_5'
#
# T-1日，挂买挂卖差的标准差
#
def factor_qyh_os5_pb2ps_std_5(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.005,'data':['ordersheet5','MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -5)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_pbid = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgBidPx.h5')
    df_poffer = IO.read_data([start_date, end_date],
                           alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgOfferPx.h5')
    df_delta = df_pbid.sub(df_poffer)
    res = df_delta.div(df_ori['close'],axis=0)
    res = pd.DataFrame(res.std(axis=1))
    res.columns = [factor_name]
    res['zcz'] = (((res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                res.reset_index()['dt'] >= '2020-08-24'))
                 | (res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    res.loc[res['zcz']==1,factor_name] = res.loc[res['zcz']==1,factor_name]/2
    res = pd.DataFrame(res[factor_name].unstack().rolling(5,1).mean().stack())
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res[[factor_name]]
