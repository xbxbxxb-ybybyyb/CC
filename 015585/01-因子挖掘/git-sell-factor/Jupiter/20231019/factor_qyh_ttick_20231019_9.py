import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231019_9'#
def factor_qyh_ttick_20231019_9(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.06}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['factor'] = (tick_df['WeightedAvgOfferPx'])/pre_close
    if zcz:
        tick_df['factor'] = (tick_df['factor']-1)/2+1
    para = 20
    if len(tick_df) > 20:
        res1 = tick_df.tail(para)['factor'].mean() + tick_df.head(para)['factor'].mean()
        res2 = tick_df.iloc[int(len(tick_df)/4):int(len(tick_df)/4*3)]['factor'].mean()
        res = res1 - res2*2
    else:
        res = 0.044
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
