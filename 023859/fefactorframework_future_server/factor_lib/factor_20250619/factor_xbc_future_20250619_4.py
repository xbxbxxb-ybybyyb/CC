import numpy as np
import pandas as pd

factor_name = 'xbc_future_20250619_4'#
def factor_xbc_future_20250619_4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    res = np.nan
    tick_df['factor'] = (tick_df['Buy1Price'] - tick_df['Sell1Price'])/tick_df['pre_close']
    if len(tick_df)>500:
        tick_df1 = tick_df.tail(500)
        tick_df2 = tick_df.tail(100)
        res = tick_df1['factor'].mean()-tick_df2['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)