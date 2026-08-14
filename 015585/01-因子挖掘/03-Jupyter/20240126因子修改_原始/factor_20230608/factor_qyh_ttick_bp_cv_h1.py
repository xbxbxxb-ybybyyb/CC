# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_bp_cv_h1'#
def factor_qyh_ttick_bp_cv_h1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.0015}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].values[0]
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.head(int(len(tick_df)/2))
    tick_df['pct'] = tick_df['WeightedAvgBidPx'] / pre
    tick_df['pct'] = tick_df['pct'].apply(lambda x : round_(x,5))
    if zcz:
        tick_df['pct'] = (tick_df['pct'] - 1)/2 + 1
    cv = tick_df['pct'].std() / abs(tick_df['pct'].mean()) if round_(tick_df['pct'].mean(),5) != 0 else 1
    factor_dict = {factor_name: cv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
