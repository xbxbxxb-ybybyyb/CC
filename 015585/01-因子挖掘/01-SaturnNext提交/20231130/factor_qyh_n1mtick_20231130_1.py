# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231130_1(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231130_1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.64}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ratiob'] = tick_df['TotalBidQty']  \
                        / (tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res = tick_df['ratiob'].quantile(0.25)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)