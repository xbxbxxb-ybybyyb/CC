# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_n1mt_ratiob_cv(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mt_ratiob_cv'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.06}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ratiob'] = tick_df['TotalBidQty']  \
                        / (tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res = tick_df['ratiob'].std() / tick_df['ratiob'].mean() if tick_df['ratiob'].mean() > 0 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)