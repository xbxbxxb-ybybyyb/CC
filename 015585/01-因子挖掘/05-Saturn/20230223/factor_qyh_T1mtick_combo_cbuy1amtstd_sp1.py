# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：0920-0925买一额标准差 + 0924-0925的跳动幅度
# score:0.07，9.7，5.2
# pj2_last_cancel_chance_price：3.88
factor_name = 'qyh_T1mtick_combo_cbuy1amtstd_sp1'#
def factor_qyh_T1mtick_combo_cbuy1amtstd_sp1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # std
    tick_df_std = tick_df[tick_df['MDTime'] >= 92000000]
    tick_df_std = tick_df_std[tick_df_std['TradingPhaseCode'] == '1']
    amt = tick_df_std['Buy1Price'] * tick_df_std['Buy1OrderQty']
    if abs(amt.mean()) > 1:
        std = amt.std() / amt.mean()
    else:
        std = np.nan
    std = (std - 0.81) / 1.4868
    # sp
     # 注册制调整
    ticker = tick_df.name[1] # 股票代码
    dt = tick_df.name[0] # 时间
    dt_str = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt_str >= '2020-08-24'))|(ticker[0:2] == '68')
    # pre
    pre = tick_df['pre_close'].mean()
     # 0925价格
    p_925 = tick_df[tick_df['TradingPhaseCode'] == '2']['LastPx'].max()
    if p_925 < 1:
        p_925 = tick_df[tick_df['TradingPhaseCode'] == '2']['Buy1Price'].max()
     # 0924价格
    p_924 = tick_df[(tick_df['MDTime'] >= 92400000) &(tick_df['TradingPhaseCode'] == '1')].head(1)['Buy1Price'].mean()
    if zcz:
        if p_924 <= pre * 0.79:
            p_924 = np.nan
    else:
        if p_924 <= pre * 0.89:
            p_924 = np.nan

    if pre > 1:
        pct_sp_1 = (p_925 - p_924)/pre * 100
    else:
        pct_sp_1 = np.nan

    if zcz:
        pct_sp_1 = pct_sp_1 / 2
    pct_sp_1 = (pct_sp_1 + 0.89)/1.5848

    factor_dict = {factor_name: std + pct_sp_1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
