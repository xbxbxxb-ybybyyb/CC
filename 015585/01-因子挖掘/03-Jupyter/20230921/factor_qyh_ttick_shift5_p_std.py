import numpy as np
import pandas as pd
# zcz
# 触发前10-5分钟的涨跌幅波动
#
#
factor_name = 'qyh_ttick_shift5_p_std'#
def factor_qyh_ttick_shift5_p_std(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.iloc[-200:-100] if len(tick_df)>200 else tick_df
    tick_df['factor'] = tick_df['LastPx']/pre_close - 1
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    res = tick_df['factor'].std()
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
