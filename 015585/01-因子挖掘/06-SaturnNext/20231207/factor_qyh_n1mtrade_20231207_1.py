# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# 最大回撤
# 21,0.059
# next_wd_t1_low_price_vol_rate:18
def factor_qyh_n1mtrade_20231207_1(trade_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtrade_20231207_1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    dt, ticker = trade_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = trade_df['pre_close'].values[0]
    trade_df = trade_df[trade_df['MDTime'] >= 93000000]
    trade_df = trade_df[trade_df['TradePrice'] > 0]
    #
    trade_df = trade_df[::-1]
    trade_df['factor'] = (trade_df['TradePrice'].cummin() - trade_df['TradePrice']) / trade_df['pre_close']
    res1 = trade_df['factor'].min()
    if zcz:
        res1 = res1/2
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)