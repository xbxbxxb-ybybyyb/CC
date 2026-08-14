import numpy as np
import pandas as pd

factor_name = 'tsq_future_20250619_4'#
def factor_tsq_future_20250619_4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    res = (tick_df['ValueTrade'] / tick_df['VolumeTrade'].replace(0,np.nan)).tail(600).std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)