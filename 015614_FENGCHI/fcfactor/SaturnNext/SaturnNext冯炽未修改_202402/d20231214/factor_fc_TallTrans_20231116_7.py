# coding: utf-8
# Author：fengchi863
# Date ：2023/5/10 21:13

import pandas as pd
import numpy as np
import datetime as dt

def fun_get_time(time1, sec_delta):
    # 计算给定时间戳time1在sec_delta秒后的时间戳
    tmp_time = dt.datetime.strptime(str(time1)[:-3], '%H%M%S')
    tmp_time2 = tmp_time + dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
    if (int(tmp_time2_str) > 113000000) & (time1 <= 113000000):
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 130000000) & (time1 >= 130000000):
        adj_tmp_time2 = tmp_time2 - dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 93000000) & (time1 >= 93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif time1 < 93000000:
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)

def factor_fc_TallTrans_20231116_7(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -------------------------------------------------突破前半小时内逐笔成交最近价格相对上次上涨的百分比--------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df.query('TradeType == 0 & TradePrice > 0')
    df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)
    df['m'] = df['MDTime'].map(lambda x: str(x)[:-2])

    start_time = max(fun_get_time(ZT_Time, -1800), 93000000)
    part_df = df.query(f'MDTime >= {start_time}')

    def calc_res(df_):
        m_px_c = df_.groupby('m')['TradePrice'].last()
        m_px_o = df_.groupby('m')['TradePrice'].first()
        res = (((m_px_c - m_px_o) / pre_close).diff() > 0).astype(int).mean()
        return res

    res = calc_res(part_df) / (calc_res(df) + 1e-4)

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    36.91 -0.06
    =====>>>> 36.916666666666664 -0.060649023845729615 1.0437222569224789 0.2835773610227396 fc_ttickab_20231102_4，zwh_20230914_007 0.5988，0.4734
    eur2mimas:
    14.208333333333334 0.03171297277912748  
    =====>>>> 14.208333333333334 0.03171297277912748 0.6699783348298873 0.3107026197156358 qyh_talltick_rlength_a25_up，xbc_20230817_4 0.55，0.4977
    """
    return pd.Series(factor_dict)