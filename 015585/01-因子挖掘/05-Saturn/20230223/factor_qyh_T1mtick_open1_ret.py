# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：0930前1个快照，相对于0925的涨跌幅
# score:基本不相关
#
factor_name = 'qyh_T1mtick_open1_ret'#
def factor_qyh_T1mtick_open1_ret(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 0925价格
    p_925 = tick_df[tick_df['TradingPhaseCode'] == '2']['LastPx'].max()
    if p_925 < 1:
        p_925 = tick_df[tick_df['TradingPhaseCode'] == '2']['Buy1Price'].max()
    # pre
    pre = tick_df['pre_close'].mean()
    # 0930价格
    p_930 = tick_df[(tick_df['MDTime'] >= 93000000) & (tick_df['MDTime'] <= 93030000)]['LastPx'].mean()
    #
    if p_925 > 1:
        ratio = (p_930 / p_925 - 1) * 100
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
