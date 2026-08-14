import numpy as np
import pandas as pd
#
# 挂买均价在触发前的值的变动
# 20分 GG
# zcz
factor_name = 'qyh_tick_b_tail_delta'#
def factor_qyh_tick_b_tail_delta(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if len(tick_df) >= 1:
        res = tick_df['WeightedAvgBidPx'].tail(1).mean() - tick_df['WeightedAvgBidPx'].min()
        res = res / pre_close
        res = res/2 if zcz else res
    else:
        res = np.nan
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
