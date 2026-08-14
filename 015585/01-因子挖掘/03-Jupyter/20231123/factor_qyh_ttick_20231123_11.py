import numpy as np
import pandas as pd
# zcz，dtj
# 最高价离群程度，平滑后
# 48，-0.068
#
factor_name = 'qyh_ttick_20231123_11'#
def factor_qyh_ttick_20231123_11(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.4}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = tick_df['HighPx'].cummax() / tick_df['pre_close']
    if zcz:
        tick_df['factor'] = (tick_df['factor']-1)/2+1
    tick_df['factor'] = tick_df['factor'] + tick_df['factor'].min()
    res = tick_df['factor'].quantile(0.99)  / tick_df['factor'].quantile(0.5) if tick_df['factor'].quantile(0.5) > 0 else np.nan
    if len(tick_df) < 20:
        res = 1.042
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)