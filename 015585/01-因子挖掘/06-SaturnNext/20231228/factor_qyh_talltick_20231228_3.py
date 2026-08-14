# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 32,-0.073,-0.08
# 涨跌幅 * 成交量对应的换手率
# xbc_20230817_3，xbc_20231221_2，zwh_20230727_002，xbc_20230810_5：25
def factor_qyh_talltick_20231228_3(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_3'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] <= 145700000]
    #
    tick_df['factor'] = (tick_df['LastPx'] / tick_df['pre_close'] - 1) * tick_df['VolumeTrade'] / (tick_df['ff_shares']+5000)
    tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    res = tick_df['factor'].std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)