# -*- coding: utf-8 -*-
import pandas as pd

#TTransaction(逐笔成交类因子)示例 Todo:注意TTransaction类因子需要控制低耗时
def factor_test_trade_factor(transaction_df, return_fillna_dic=False):
    factor_name = 'test_trade_factor'

    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df=transaction_df[transaction_df['TradePrice']>0] #去除深圳撤单的逐笔成交数据
    transaction_df = transaction_df[transaction_df['MDTime'] >=93000000] #选择连续竞价阶段的逐笔成交数据
    amt = transaction_df['TradeMoney'].sum()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

