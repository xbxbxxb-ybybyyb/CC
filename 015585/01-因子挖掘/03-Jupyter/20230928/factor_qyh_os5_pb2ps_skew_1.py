import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_os5_pb2ps_skew_1'
# T-1日，挂买挂卖差的偏度
# 5,0.01
#
def factor_qyh_os5_pb2ps_skew_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0,'data':['ordersheet5','MD']}
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
    res = pd.DataFrame(df_delta.skew(axis=1))
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res[[factor_name]]
