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

def factor_fc_next1mTrans_20231109_11(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # -----------------------------------------------------高价格区间换手/低价格区间换手----------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    def calc_res(df, pct1, pct2):
        part_df = df.query(f'{pct1} <= TradePrice <= {pct2}')
        turn = part_df['TradeQty'] / part_df['ff_shares']
        return turn.sum()

    dt, Ticker = df.index[0]
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    df = df.query('TradeType == 0 & TradePrice > 0')
    df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)

    pct_list = [0, 0.01, 0.1]
    pct_list = list(map(lambda x: x * (zcz + 1), pct_list))
    price_list = list(map(lambda x: np.floor(pre_close * 100 * (1 + x) + 0.5 + 1e-8) / 100, pct_list))

    ret = calc_res(df, price_list[1], price_list[2]) / (calc_res(df, price_list[0], price_list[1]) + 0.01)

    factor_dict = {factor_name: ret}
    # ---------------------------------------------------------------------------------------------------------------
    """
    不同涨跌幅区间内换手率之比
    13.33 -0.05  
    =====>>>> 13.333333333333334 -0.051957224199872504 1336.1924915028876 6639.414645455443 Next_o2pre，next_wd_k1_ask_pct 0.6975，0.6042
    """
    return pd.Series(factor_dict)