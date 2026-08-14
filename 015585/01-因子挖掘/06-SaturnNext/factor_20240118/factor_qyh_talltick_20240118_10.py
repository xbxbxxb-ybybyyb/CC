# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 28,0.057,0.071
# 尾盘上影线的中位数
def factor_qyh_talltick_20240118_10(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20240118_10'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    # tick_df['vwap'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    # tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 143000000]
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    #
    tick_df['pcummax'] = tick_df['LastPx'].cummax()
    tick_df['pcummin'] = tick_df['LastPx'].cummin()
    tick_df['amp'] = tick_df['pcummax'] - tick_df['pcummin']
    tick_df['amp'] = tick_df['amp'].apply(lambda x: np.nan if abs(x)<0.0001 else x)
    tick_df['factor'] = (tick_df['pcummax'] - tick_df['LastPx'])\
                      / tick_df['amp']
    # tick_df = tick_df[(tick_df['Sell1Price'] > 0) | (tick_df['Buy1Price'] > 0)]
    # if zcz:
    #     tick_df['factor'] = tick_df['factor']/2
    #
    res = tick_df['factor'].median()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)