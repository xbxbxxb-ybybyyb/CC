import numpy as np
import pandas as pd
#
# 价格凸性
#
factor_name = 'qyh_tick_conv'#
def factor_qyh_tick_conv(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.05}
    pre_close = tick_df['pre_close'].values[0]
    trans_df = tick_df[tick_df['MDTime'] >= 93000000]
    # trans_df = trans_df[trans_df['TradePrice'] != trans_df['TradePrice'].shift(1)]
    trans_df['LastPx_diff1'] = trans_df['LastPx'] - trans_df['LastPx'].shift(1)
    trans_df['LastPx_diff2'] = trans_df['LastPx_diff1'] - trans_df['LastPx_diff1'].shift(1)
    res = trans_df['LastPx_diff2'].max() / pre_close
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
