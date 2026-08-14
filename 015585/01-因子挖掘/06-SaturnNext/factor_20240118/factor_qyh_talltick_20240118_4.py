# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 挂卖的首末差异/全天交易额
# 24，0.058，0.062
# qyh_talltick_cleanb2tt_ch：19，wj_last_se_offer：12
def factor_qyh_talltick_20240118_4(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20240118_4'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    # tick_df = tick_df[tick_df['ValueTrade'] > 0]
    tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    #
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['sell_amt'])/tick_df['ValueTrade'].sum()
    res = tick_df['factor'].tail(1).mean() - tick_df['factor'].head(1).mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)