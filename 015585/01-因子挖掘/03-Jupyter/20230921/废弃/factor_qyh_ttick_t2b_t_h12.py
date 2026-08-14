import numpy as np
import pandas as pd
#
# 成交和买均的距离在中期和触发前的差
# 0.137,81
# xbc_20230914_7:85
factor_name = 'qyh_ttick_t2b_t_h12'#
def factor_qyh_ttick_t2b_t_h12(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.019}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = (tick_df['LastPx'] - tick_df['WeightedAvgBidPx']) / pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    n = 1
    if len(tick_df)>n+1:
        res1 = tick_df.head(int(len(tick_df)/(n+1)))['factor'].tail(1).values[0]
        res2 = tick_df['factor'].tail(1).values[0]
        res = res1 - res2
    else:
        res = -0.066
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
