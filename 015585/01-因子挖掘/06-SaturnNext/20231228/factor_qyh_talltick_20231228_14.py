# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 上影线在活跃/不活跃的差异
# 19，0.05，0.065
#
def factor_qyh_talltick_20231228_14(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_14'
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
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    #
    # tick_df = tick_df[(tick_df['Sell1Price'] > 0) & (tick_df['Buy1Price'] > 0)]
    # if zcz:
    #     tick_df['factor'] = tick_df['factor']/2
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df2 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    res = []
    for tick_df_ in [tick_df1,tick_df2]:
        tick_df_['pcummax'] = tick_df_['LastPx'].cummax()
        tick_df_['pcummin'] = tick_df_['LastPx'].cummin()
        tick_df_['amp'] = tick_df_['pcummax'] - tick_df_['pcummin']
        tick_df_['amp'] = tick_df_['amp'].apply(lambda x: np.nan if abs(x)<0.0001 else x)
        tick_df_['syx1'] = (tick_df_['pcummax'] - tick_df_['LastPx'])\
                          / tick_df_['amp']
        tick_df_['factor'] = tick_df_['syx1']
        res_ = tick_df_['factor'].sum()
        res.append(res_)
    res = res[0] - res[1]
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)