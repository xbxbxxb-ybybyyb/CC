# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj,zcz
# 相对净委买在价格较低时的min
# 40,0.077,0.092
# next_sss_tk1m_1oia_min:38
def factor_qyh_n1mtick_20231221_3(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231221_3'
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
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    p = round_(tick_df['LastPx'].quantile(0.25),5)
    tick_df = tick_df[tick_df['LastPx'] < p] if p > 0 else tick_df
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    #
    res = tick_df['factor'].min()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)