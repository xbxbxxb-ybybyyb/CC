# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：跳开幅度：集合竞价0925 - 0920
# score:3.3,0.05
# pj2_last_cancel_chance_price:3.88
factor_name = 'qyh_T1mtick_pct_sp_5'#skip price
def factor_qyh_T1mtick_pct_sp_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 注册制调整
    ticker = tick_df.name[1] # 股票代码
    dt = tick_df.name[0] # 时间
    dt_str = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt_str >= '2020-08-24'))|(ticker[0:2] == '68')
    # pre
    pre = tick_df['pre_close'].mean()
    # 925
    p_925 = tick_df[tick_df['TradingPhaseCode'] == '2']['LastPx'].max()
    if p_925 < 1:
        p_925 = tick_df[tick_df['TradingPhaseCode'] == '2']['Buy1Price'].max()
    # 920
    p_920 = tick_df[(tick_df['MDTime'] >= 92000000) &(tick_df['TradingPhaseCode'] == '1')].head(1)['Buy1Price'].mean()
    if zcz:
        if p_920 <= pre * 0.79:
            p_920 = np.nan
    else:
        if p_920 <= pre * 0.89:
            p_920 = np.nan
    #
    if pre > 1:
        pct_sp_5 = (p_925 - p_920)/pre * 100
    else:
        pct_sp_5 = np.nan

    if zcz:
        pct_sp_5 = pct_sp_5 / 2
    factor_dict = {factor_name: pct_sp_5}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
