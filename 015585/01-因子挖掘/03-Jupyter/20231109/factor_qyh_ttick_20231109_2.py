import numpy as np
import pandas as pd
# zcz,dtj
# 集合竞价和开盘后价格的差异
# -0.11,54
#
factor_name = 'qyh_ttick_20231109_2'#
def factor_qyh_ttick_20231109_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df1 = tick_df[tick_df['MDTime'] < 93000000]
    tick_df1 = tick_df1.head(int(len(tick_df1)/2)) if len(tick_df1)> 10 else tick_df1
    res1 = tick_df1.tail(1)['Buy1Price'].mean()/pre_close
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  #
    tick_df = tick_df.head(int(len(tick_df)/2)) if len(tick_df)>10 else tick_df
    res2 = tick_df.tail(1)['Buy1Price'].mean()/pre_close
    res = res1 - res2
    if zcz:
        res = res/2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)