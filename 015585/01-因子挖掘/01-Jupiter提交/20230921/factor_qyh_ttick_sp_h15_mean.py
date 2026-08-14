import numpy as np
import pandas as pd
# zcz,dtj
# 挂卖均价在前1/4的均值
# 56,0.086
#
factor_name = 'qyh_ttick_sp_h15_mean'#
def factor_qyh_ttick_sp_h15_mean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1.05}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.head(300) if len(tick_df) > 300 else tick_df.head(int(len(tick_df)/2))
    tick_df['factor'] = tick_df['WeightedAvgOfferPx'] / pre_close
    if zcz:
        tick_df['factor'] = (tick_df['factor'] - 1)/2+1
    res = tick_df['factor'].mean()
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
