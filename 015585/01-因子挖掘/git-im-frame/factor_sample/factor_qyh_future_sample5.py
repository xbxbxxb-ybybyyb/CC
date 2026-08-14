import numpy as np
import pandas as pd

factor_name = 'qyh_future_sample5'#
def factor_qyh_future_sample5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = tick_df['LastPx'] - tick_df['Buy1Price']
    res = tick_df['factor'].tail(60).std()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
