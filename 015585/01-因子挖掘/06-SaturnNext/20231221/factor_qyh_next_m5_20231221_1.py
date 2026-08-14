import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj,zcz
# 27,0.056
# 非早盘柱长/K线总长度的5日均值
factor_name = 'qyh_next_m5_20231221_1'
def factor_qyh_next_m5_20231221_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['MD','minute5']}
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
    df_open = IO.read_data([start_date,end_date],
                           alt = '/data/group/800463/data/generalStrong/minute5/open.h5')
    df_res = abs(df_close - df_open)/(df_high - df_low + 1e-2)
    df_res = df_res.iloc[:,10:]
    res = pd.DataFrame(df_res.mean(axis=1))
    res.columns = [factor_name]
    # res['zcz'] = (((res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             res.reset_index()['dt'] >= '2020-08-24'))
    #              | (res.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    # res.loc[res['zcz']==1,factor_name] = res.loc[res['zcz']==1,factor_name]/2
    res[factor_name] = res[factor_name].unstack().rolling(5,5).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return res[[factor_name]]
