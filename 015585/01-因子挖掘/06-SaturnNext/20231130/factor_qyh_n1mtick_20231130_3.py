# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
#
#
#
def factor_qyh_n1mtick_20231130_3(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231130_3'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 53}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    b2ttran = (tick_df['buy_amt'])/(tick_df['ValueTrade'].sum()+1)
    res = b2ttran.sum()
    if res == 0:
        res = np.nan
    #
    tick_df['ratiob'] = tick_df['TotalBidQty']  \
                        / (tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res2 = tick_df['ratiob'].min()
    if res2 > 0.5:
        res = res + 10/res2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)