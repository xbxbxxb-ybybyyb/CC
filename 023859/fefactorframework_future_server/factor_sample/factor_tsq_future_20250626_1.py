import numpy as np
import pandas as pd

factor_name = 'tsq_future_20250626_1'#
def factor_tsq_future_20250626_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ret'] = 100*tick_df['LastPx'].pct_change()
    tick_df['VolumeTrade'] = (tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0))/10000
    tick_df = tick_df.tail(600)
    res = (tick_df['ret']*tick_df['VolumeTrade']).sum() / (1e-6+tick_df['VolumeTrade'].sum())
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)