import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231102_5'#
def factor_qyh_ttick_20231102_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.47}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['factor'] = (tick_df['Sell1Price'] - tick_df['WeightedAvgOfferPx']) / pre_close
    if zcz:
        tick_df['factor'] = (tick_df['factor']) / 2
    #
    tick_df1 = tick_df.head(20)
    tick_df2 = tick_df.tail(20)
    res1 = tick_df1['factor'].std() / (tick_df1['factor'].mean()+1e-5)
    res2 = tick_df2['factor'].std() / (tick_df2['factor'].mean()+1e-5)
    factor_dict = {factor_name: res1 - res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)


