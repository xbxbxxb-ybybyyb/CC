import numpy as np
import pandas as pd
# zcz,dtj
# 买1峰度
# -0.1,61
#
factor_name = 'qyh_ttick_b1_kurt'#
def factor_qyh_ttick_b1_kurt(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0.5}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.tail(len(tick_df)-200) if len(tick_df) > 200 else tick_df
    res = tick_df['Buy1Price'].kurt()
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
