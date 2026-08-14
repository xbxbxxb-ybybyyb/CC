# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# test
# test
# 930_after_all_all_0_bigger_all_cleanb2ttran_nostd_m2m_nocompare
#
def factor_qyh_talltick_cleanb2tran_m2m(tick_df, return_fillna_dic=False):
    factor_name = 'factor_qyh_talltick_cleanb2tran_m2m'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 65}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    cleanb2ttran = (tick_df['buy_amt'] - tick_df['sell_amt']) / tick_df['ValueTrade'].sum()#
    cleanb2ttran = cleanb2ttran + cleanb2ttran.min()
    res = cleanb2ttran.max() / cleanb2ttran.mean() if cleanb2ttran.mean() > 0 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)