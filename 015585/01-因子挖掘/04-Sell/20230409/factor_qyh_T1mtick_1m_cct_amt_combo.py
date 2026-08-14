# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：0931，成交量分布因子：amt集中度与量价相关性
# score:0.046,9,6
# 无
factor_name = 'qyh_T1mtick_1m_cct_amt_combo'#
def factor_qyh_T1mtick_1m_cct_amt_combo(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.2}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    # tick_df['p'] = tick_df['amt'] / tick_df['vol']
    # p_max = tick_df['p'].max()
    # p_min = tick_df['p'].min()
    # def get_p_group(price,n=16):
    #     delta = (p_max - p_min)/n
    #     for i in range(n):
    #         if price <= p_min + ((i+1) * delta):
    #             if i+1 <=(n/2):
    #                 return i+1
    #             else:
    #                 return n-(i+1)
    # if p_max - p_min > 0.1:
    #     tick_df['p_group'] = tick_df['p'].apply(lambda x:get_p_group(x))
    #     df_p_amt = tick_df.groupby('p_group')['amt'].sum()
    #     ratio_1 = (df_p_amt ** 2).sum() / (df_p_amt.sum()**2)
    # else:
    #     ratio_1 = 0.2
    ratio_2 = (tick_df['amt'] ** 2).sum() / tick_df['amt'].sum()**2
    corr = pd.concat([(tick_df['amt'] / tick_df['vol']).shift(-1),tick_df['vol']],axis =1).corr(method = 'spearman').iloc[0,1]
    factor_dict = {factor_name: ((ratio_2 - 0.2) / 0.08) - ((abs(corr) - 0.256) / 0.179)}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
