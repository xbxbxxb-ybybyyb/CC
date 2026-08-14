import numpy as np
import pandas as pd
#
# 最后150个tick中，累计high-low的标准差
# 85,-0.126 # 填充值用-2可以另一组；去掉除以std可以86;tick_df = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]为58不高相关
# qyh_ttick_20231019_1等5个
factor_name = 'qyh_ttick_20231102_2'#
def factor_qyh_ttick_20231102_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -2}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.25)]
    tick_df['factor'] = (tick_df['HighPx'] - tick_df['LowPx']) / pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor'] / 2
    #
    para = 180
    tick_df = tick_df.tail(para) if len(tick_df) > para else tick_df.tail(int(len(tick_df) / 3*2))
    res = tick_df['factor'].std() / (tick_df['factor'].mean() + 1e-5)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)