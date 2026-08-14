import numpy as np
import pandas as pd

factor_name = 'tsq_future_20250626_2'#
def factor_tsq_future_20250626_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ret'] = tick_df['LastPx'].pct_change()
    tick_df = tick_df.tail(600)
    res = len(tick_df[tick_df['ret']>0]) / (1e-6+len(tick_df))
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)