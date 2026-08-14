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

def factor_fc_trans_20231019_14(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------突破前最近90笔订单净买入金额-------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]

    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).replace({True: 1, False: -1})
    df['act_buy_amt'] = df['buy_flag'] * df['TradeMoney']
    res = df.iloc[-min(len(df), 90):]['act_buy_amt'].mean()

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    79.83 -0.108
    =====>>>> 79.83333333333333 0.10894758743609173 18937.098849188955 21526.893338522306 xbc_dir_money，skk_TTrans_order_100_s_ratio_new，sundc_t_tran_39 0.9834，0.6156，0.6086
    """
    return pd.Series(factor_dict)