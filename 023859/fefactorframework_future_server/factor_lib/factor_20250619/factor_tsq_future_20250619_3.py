import numpy as np
import pandas as pd

factor_name = 'tsq_future_20250619_3'#
def factor_tsq_future_20250619_3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    res = tick_df['LastPx'].corr(tick_df['VolumeTrade'], method='spearman')
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)