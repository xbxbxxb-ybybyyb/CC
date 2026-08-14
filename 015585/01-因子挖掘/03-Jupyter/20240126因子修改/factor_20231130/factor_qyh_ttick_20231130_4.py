import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231130_4'#
def factor_qyh_ttick_20231130_4(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] =  0.5*(tick_df['HighPx'] + tick_df['LowPx']) / tick_df['pre_close']
    if zcz:
        tick_df['factor'] = (tick_df['factor']-1) / 2+1
    #
    tick_df['factor'] = tick_df['factor'] - tick_df['factor'].min()
    res = tick_df['factor'].max() / tick_df['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)