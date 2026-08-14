# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：t-1日涨停挂单峰值以后，新增挂买/新增挂卖
# score:0.04,6
# 无
factor_name = 'qyh_lzo_aztmax_ratio_b2s'#
def factor_qyh_lzo_aztmax_ratio_b2s(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2}
    # 0930以后
    order_df = order_df[order_df['MDTime'] >= 93000000]
    #
    pre_close = round(order_df['pre_close'].mean(),3)
    ticker = order_df['HTSCSecurityID'][0]
    dt = order_df['MDDate'][0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    order_df['min'] = order_df['MDTime'].apply(lambda x:int(str(x)[:-5]))
    # 峰值时间
    order_df_zt = order_df[order_df['OrderPrice'] >= p_zt]
    order_df_zt = order_df_zt.groupby('min')['OrderQty'].sum()
    t = order_df_zt.idxmax()
    #
    order_df_azt = order_df[(order_df['min'] > t) & (order_df['OrderBSFlag'] == 1)]#涨停以后的部分
    order_df_amt = order_df_azt['OrderQty'] * order_df_azt['OrderPrice']
    amt_1 = order_df_amt.sum()
    order_df_azt = order_df[(order_df['min'] > t) & (order_df['OrderBSFlag'] == 2)]#涨停以后的部分
    order_df_amt = order_df_azt['OrderQty'] * order_df_azt['OrderPrice']
    amt_2 = order_df_amt.sum()
    if amt_2 > 10:
        ratio = amt_1 / amt_2
    else:
        ratio = np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
