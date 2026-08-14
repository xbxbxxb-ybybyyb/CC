import numpy as np
import pandas as pd

factor_name = 'qyh_future_sample10'#
def factor_qyh_future_sample10(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'].diff()
    tick_df['factor'] = (tick_df['VolumeTrade'] + tick_df['OpenInterest'].diff()) / (abs(tick_df['VolumeTrade']) + abs(tick_df['OpenInterest'].diff()))
    res = tick_df['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)