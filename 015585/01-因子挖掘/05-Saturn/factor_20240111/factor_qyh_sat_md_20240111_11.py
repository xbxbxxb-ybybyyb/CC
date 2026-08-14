import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# not dtj

factor_name = 'qyh_sat_md_20240111_11'
def factor_qyh_sat_md_20240111_11(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['ordersheet5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    #
    bid_vol = IO.read_data([start_date,end_date],alt = '/data/group/800463/data/generalStrong/ordersheet5/TotalBidQty.h5')
    offer_vol = IO.read_data([start_date, end_date],alt='/data/group/800463/data/generalStrong/ordersheet5/TotalOfferQty.h5')
    # bid_price = IO.read_data([start_date, end_date],alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgBidPx.h5')
    # offer_price = IO.read_data([start_date, end_date],alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgOfferPx.h5')
    # bid_amt = bid_vol * bid_price
    # offer_amt = offer_vol * offer_price
    bid_vol = bid_vol.iloc[:,:-1]
    offer_vol = offer_vol.iloc[:,:-1]
    strength = ((bid_vol - offer_vol) / (bid_vol + 1)).mean(axis=1)
    # strength = ((bid_amt- offer_amt).divide((offer_amt.sum(1) + bid_amt.sum(1)),axis=0)).max(axis = 1)
    factor_df = pd.DataFrame()
    factor_df[factor_name] = strength
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df