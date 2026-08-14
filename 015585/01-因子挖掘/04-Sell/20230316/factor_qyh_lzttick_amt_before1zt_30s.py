# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：首次涨停前30s的成交额(首次上板力度)
# score:-0.048,7
# 无
factor_name = 'qyh_lzttick_amt_before1zt_30s'#
def factor_qyh_lzttick_amt_before1zt_30s(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 12694214}
    p_zt = tick_df['LastPx'].max()
    # tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    # 首次涨停时间
    time = tick_df[tick_df['LastPx'] == p_zt]['MDTime'].min()
    amt_df = tick_df[tick_df['MDTime'] <= time]['TotalValueTrade']
    if len(amt_df) >= 10:
        amt = amt_df.tail(10).max() - amt_df.tail(10).min()
    else:
        amt = amt_df.sum()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
