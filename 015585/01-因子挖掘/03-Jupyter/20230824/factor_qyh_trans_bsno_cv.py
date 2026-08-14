import numpy as np
import pandas as pd
# dtj
# 买卖订单差序列的标准差
#
factor_name = 'qyh_trans_bsno_cv'#
def factor_qyh_trans_bsno_cv(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.05}
    # pre_close = trans_df['pre_close'].values[0]
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    trans_df = trans_df[trans_df['TradePrice'] > 0]
    trans_df['delno'] = trans_df['TradeBuyNo'] - trans_df['TradeSellNo']
    trans_df['delno'] = trans_df['delno'] - trans_df['delno'].min()
    # delno_mean = (trans_df['delno'] * trans_df['TradeMoney']).sum() / trans_df['TradeMoney'].sum()
    # res1 = (trans_df['TradeMoney'] * ((trans_df['delno'] - delno_mean)**2)).sum() ** 0.5
    # res2 = trans_df['TradeMoney'].sum() ** 0.5
    res = trans_df['delno'].std() / trans_df['TradeBuyNo'].quantile(0.7)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
