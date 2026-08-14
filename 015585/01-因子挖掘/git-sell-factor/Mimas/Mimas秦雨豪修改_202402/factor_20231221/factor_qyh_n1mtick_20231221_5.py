# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231221_5(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231221_5'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5}
    import decimal
    def round_(x, n=0):
        x = x + 1e-10
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    p = round_(tick_df['LastPx'].quantile(0.3),5)
    tick_df = tick_df[tick_df['LastPx'] < p] if p > 0 else tick_df
    tick_df['factor'] = tick_df['NumTrades'] - tick_df['NumTrades'].shift(1).fillna(0)
    #
    res = tick_df['factor'].tail(1).mean() - tick_df['factor'].head(1).mean() if not tick_df.empty else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)