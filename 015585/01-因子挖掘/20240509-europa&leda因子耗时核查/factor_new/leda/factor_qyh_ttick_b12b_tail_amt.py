# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_b12b_tail_amt'#
def factor_qyh_ttick_b12b_tail_amt(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01}
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
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,5))
    tick_df1 = tick_df[tick_df['ValueTrade'] > (round_(tick_df['ValueTrade'].quantile(0.75),5)-1e-6)]
    tick_df2 = tick_df[tick_df['ValueTrade'] < (round_(tick_df['ValueTrade'].quantile(0.25),5)+1e-6)]
    #
    pct1 = ((tick_df1['Buy1Price'] - tick_df1['WeightedAvgBidPx']) / pre).tail(1).mean()
    pct2 = ((tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']) / pre).tail(1).mean()
    if zcz:
        pct1 = pct1/2
        pct2 = pct2/2
    factor_dict = {factor_name: pct1 - pct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
