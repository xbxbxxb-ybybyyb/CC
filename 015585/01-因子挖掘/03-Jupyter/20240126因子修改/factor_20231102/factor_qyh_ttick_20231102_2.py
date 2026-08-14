import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231102_2'#
def factor_qyh_ttick_20231102_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.002}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['factor'] = (tick_df['WeightedAvgBidPx'])/pre_close
    if zcz:
        tick_df['factor'] = (tick_df['factor']-1)/2+1
    tick_df1 = tick_df.head(int(len(tick_df)/4))
    tick_df2 = tick_df.tail(int(len(tick_df)/4))
    res1 = tick_df1['factor'].quantile(0.1)
    res2 = tick_df2['factor'].quantile(0.1)
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


