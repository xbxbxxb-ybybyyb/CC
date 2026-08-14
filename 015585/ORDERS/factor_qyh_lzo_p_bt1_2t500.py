# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日涨停挂单峰值以前的挂单均价对应的涨跌幅 - 最后500单对应的涨跌幅
# 0.077,11
# wu
factor_name = 'qyh_lzo_p_bt1_2t500'#
def factor_qyh_lzo_p_bt1_2t500(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.035}
    order_df = order_df[order_df['MDTime'] >= 93000000]
    order_df['min'] = order_df['MDTime'].apply(lambda x:int(str(x)[:-5]))
    pre_close = order_df['pre_close'].mean()
    ticker = order_df['HTSCSecurityID'][0]
    dt = order_df['MDDate'][0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    if zcz:
        p_zt = np.floor(pre_close * 100 * 1.2 + 0.5) / 100
    else:
        p_zt = np.floor(pre_close * 100 * 1.1 + 0.5) / 100
    # 峰值时间
    order_df_zt = order_df[order_df['OrderPrice'] >= p_zt]
    order_df_zt = order_df_zt.groupby('min')['OrderQty'].sum()
    t = order_df_zt.idxmax()
    #
    order_df = order_df[order_df['min'] < t]
    order_df1 = order_df.head(int(len(order_df)-500))
    order_df2 = order_df.tail(500)
    p1 = (order_df1['OrderQty'] * order_df1['OrderPrice']).sum() / (order_df1['OrderQty'].sum())
    p2 = (order_df2['OrderQty'] * order_df2['OrderPrice']).sum() / (order_df2['OrderQty'].sum())
    pre = order_df['pre_close'].max()
    if pre > 0.1:
        ratio1 = p1/pre - 1
        ratio2 = p2/pre - 1
        if zcz:
            ratio1 = ratio1 / 2
            ratio2 = ratio2 / 2
        ratio = ratio1 - ratio2
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
