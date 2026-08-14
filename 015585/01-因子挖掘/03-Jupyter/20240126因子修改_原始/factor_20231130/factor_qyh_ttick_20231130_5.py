import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231130_5'#
def factor_qyh_ttick_20231130_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.045}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df1 = tick_df.head(20)
    tick_df2 = tick_df.tail(20)
    #
    tick_df1['h'] = (tick_df1['LastPx'] / tick_df1['pre_close']).cummax()-1
    tick_df2['h'] = (tick_df2['LastPx'] / tick_df2['pre_close']).cummax()-1
    if zcz:
        tick_df1['h'] = tick_df1['h']/2
        tick_df2['h'] = tick_df2['h']/2
    #
    res1 = tick_df1['h'].head(1).mean() - tick_df1['h'].tail(1).mean()
    res2 = tick_df2['h'].head(1).mean() - tick_df2['h'].tail(1).mean()
    res = res1 - res2
    if len(tick_df)<20:
        res = res + 0.12
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)