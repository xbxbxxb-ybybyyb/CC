# -*- coding: utf-8 -*-
# @Time    : 2023/05/11 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_ps_tail'#
def factor_qyh_ttick_ps_tail(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.099}
    # zcz
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    bj = ticker[-2:] == 'BJ'
    pre = tick_df['pre_close'].values[0]
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    #
    p1 = tick_df[(tick_df['MDTime']>=92500000) & (tick_df['LastPx'] > 1)].head(1)['LastPx'].mean()
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    p = (tick_df['WeightedAvgOfferPx'] / pre).tail(1).mean()-1
    p = round_(p,5)
    if zcz == 1:
        p = p/2
    elif bj:
        p = p/3
    #
    if not p > 0:
        if zcz:
            p = 1.2*1.05 - p1/pre*0.05
            # p = (p-1)/2+1
            p = (p-1)/2
        elif bj:
            p = 1.3*1.05 - p1/pre*0.05
            # p = (p-1)/2+1
            p = (p-1)/3
        else:
            p = 1.1*1.05 - p1/pre*0.05 - 1
    # 太低认为无效
    if p < 0.0923:
        p = 0.0998
    factor_dict = {factor_name: p}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

