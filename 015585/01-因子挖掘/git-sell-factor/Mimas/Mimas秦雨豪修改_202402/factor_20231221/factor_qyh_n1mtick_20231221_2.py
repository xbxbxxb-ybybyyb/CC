# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231221_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231221_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
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
    tick_df['VolumeTrade'] = tick_df['VolumeTrade'].apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93015000]
    res = tick_df['ValueTrade'].head(1).values[0] if not tick_df.empty else np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)