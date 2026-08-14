import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_os5m5_20231214_2'
# dtj,zcz
# 过去5日，vwap-挂买的均值
#
def factor_qyh_next_os5m5_20231214_2(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['ordersheet5','MD','minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -5)[0])
    # df_ori = IO.read_data([start_date, end_date],
    #                       columns=['close'],
    #                       alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_pbid = IO.read_data([start_date,end_date],
    #                        alt = '/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgBidPx.h5')
    # df_poffer = IO.read_data([start_date, end_date],
    #                        alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgOfferPx.h5')
    # df_amt = IO.read_data([start_date,end_date],
    #                        alt = '/data/group/800463/data/generalStrong/minute5/amt.h5')
    # df_vol = IO.read_data([start_date,end_date],
    #                        alt = '/data/group/800463/data/generalStrong/minute5/volume.h5')
    df_close = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/minute5/close.h5')
    df_high = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/minute5/high.h5')
    df_low = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/minute5/low.h5')
    # df_vwap = df_amt.div(df_vol)
    df_delta = df_close.sub(0.5*(df_high+df_low))
    res = df_delta.div(df_close)
    res = pd.DataFrame(res.mean(axis=1))
    res.columns = [factor_name]
    res['zcz'] = (((res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                res.reset_index()['dt'] >= '2020-08-24'))
                 | (res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    res.loc[res['zcz']==1,factor_name] = res.loc[res['zcz']==1,factor_name]/2
    res[factor_name] = res[factor_name].unstack().rolling(10,1).median().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return res[[factor_name]]
