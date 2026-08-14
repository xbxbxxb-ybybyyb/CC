import numpy as np
import pandas as pd
# dtj
# 前1/3订单的振幅
# 53,0.089
factor_name = 'qyh_trans_h1_amp'#
def factor_qyh_trans_h1_amp(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.05}
    pre_close = trans_df['pre_close'].values[0]
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    trans_df = trans_df[trans_df['TradePrice'] > 0]
    trans_df = trans_df.head(int(len(trans_df)/3)) if len(trans_df) > 2 else trans_df
    res = (trans_df['TradePrice'].max() - trans_df['TradePrice'].min()) / pre_close
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
