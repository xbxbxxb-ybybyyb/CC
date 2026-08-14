import numpy as np
import pandas as pd

factor_name = 'qyh_future_sample4'#
def factor_qyh_future_sample4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'].diff()
    res = tick_df['VolumeTrade'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)