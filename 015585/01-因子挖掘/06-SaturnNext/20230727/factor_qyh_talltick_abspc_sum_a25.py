# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
#
# 成交较低时的价格变化路径
# 1,-0.01
def factor_qyh_talltick_abspc_sum_a25(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_abspc_sum_a25'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['absp'] = abs(tick_df['LastPx'] - tick_df['LastPx'].shift(1))
    tick_df = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    absp_sum = tick_df['absp'].sum() / pre
    factor_dict = {factor_name: absp_sum}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

