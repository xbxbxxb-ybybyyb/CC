import numpy as np
import pandas as pd

factor_name = 'tsq_future_20250619_5'#
def factor_tsq_future_20250619_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    res = ((tick_df[[f'Buy{i}OrderQty' for i in range(1,6)]].sum(axis=1) - tick_df[[f'Sell{i}OrderQty' for i in range(1,6)]].sum(axis=1))\
        /(1e-6 + tick_df[[f'Buy{i}OrderQty' for i in range(1,6)]].sum(axis=1) + tick_df[[f'Sell{i}OrderQty' for i in range(1,6)]].sum(axis=1))).tail(600).mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)