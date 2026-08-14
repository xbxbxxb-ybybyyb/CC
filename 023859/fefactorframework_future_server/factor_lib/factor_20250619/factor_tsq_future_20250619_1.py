import numpy as np
import pandas as pd

factor_name = 'tsq_future_20250619_1'#
def factor_tsq_future_20250619_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    res = (tick_df['HighPx'] / tick_df['LowPx'].replace(0,np.nan) - 1).std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)