import numpy as np
import pandas as pd
# 主动买入金额用每秒卖出金额加权
# 逻辑：
#
factor_name = 'qyh_trans_skline_buyamt_vwaps'#
def factor_qyh_trans_skline_buyamt_vwaps(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.66}
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    trans_df['MDTime_s'] = trans_df['MDTime'].apply(lambda x:int(str(x)[:-3]))
    res1 = trans_df.groupby('MDTime_s')['TradeMoney'].sum()
    res2 = trans_df[trans_df['TradeBSFlag'] == 2].groupby('MDTime_s')['TradeMoney'].sum()
    res = (res1 * res2).sum() / res2.sum()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
