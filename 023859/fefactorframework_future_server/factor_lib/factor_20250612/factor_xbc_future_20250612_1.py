import numpy as np
import pandas as pd

factor_name = 'xbc_future_20250612_1'#
def factor_xbc_future_20250612_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    res = np.nan
    tick_df['LastPx_ratio'] = tick_df['LastPx']/tick_df['pre_close']
    if len(tick_df)>200:
        tick_df1 = tick_df.tail(100)
        tick_df2 = tick_df.tail(200)

        res = tick_df1['LastPx_ratio'].std()-tick_df2['LastPx_ratio'].std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)