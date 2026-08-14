# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_n1mt_ratiob_cv(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mt_ratiob_cv'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.06}
    import decimal
    def round_(x, n=0):
        x = x + 1e-8
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ratiob'] = tick_df['TotalBidQty']  \
                        / (tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res = tick_df['ratiob'].std() / tick_df['ratiob'].mean() if round_(tick_df['ratiob'].mean(),6) > 0 else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)