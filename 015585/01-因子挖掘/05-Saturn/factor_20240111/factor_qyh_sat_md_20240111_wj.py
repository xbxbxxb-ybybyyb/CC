import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
#
#
factor_name = 'qyh_sat_md_20240111_wj'
def factor_qyh_sat_md_20240111_wj(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['ordersheet5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    #
    bid_vol = IO.read_data([start_date,end_date],alt = '/data/group/800463/data/generalStrong/ordersheet5/TotalBidQty.h5')
    offer_vol = IO.read_data([start_date, end_date],alt='/data/group/800463/data/generalStrong/ordersheet5/TotalOfferQty.h5')
    bid_price = IO.read_data([start_date, end_date],alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgBidPx.h5')
    offer_price = IO.read_data([start_date, end_date],alt='/data/group/800463/data/generalStrong/ordersheet5/WeightedAvgOfferPx.h5')
    amt = IO.read_data([start_date, end_date],alt='/data/group/800463/data/generalStrong//minute5/amt.h5')
    amt = amt.replace(0,np.nan)
    bid_amt = bid_vol * bid_price
    offer_amt = offer_vol * offer_price
    # strength = (bid_amt.sum(1)  - offer_amt.sum(1)) / (amt.sum(1))
    strength = ((bid_amt - offer_amt)/bid_amt).max(1)
    factor_df = pd.DataFrame()

    factor_df[factor_name] = strength
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df