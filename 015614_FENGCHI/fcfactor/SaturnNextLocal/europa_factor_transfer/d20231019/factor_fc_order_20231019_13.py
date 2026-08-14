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

def factor_fc_order_20231019_13(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # --------------------------------------------------突破前短区间与全天vwap的比值-------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].max()
    ZT_Time = df['MDTime'].max()
    df = df[df['OrderType'].isin([1, 2])]
    df = df.query('MDTime >= 93000000')
    df = df.query('OrderBSFlag==2')
    if len(df) == 0: return pd.Series({factor_name: np.nan})

    sml, big = df['OrderPrice'].quantile([1.0, 0.95])
    sml_part = df.query(f'OrderPrice <= {sml}')
    big_part = df.query(f'OrderPrice >= {big}')

    sml_vwap = (sml_part['OrderQty'] * sml_part['OrderPrice']).sum() / sml_part['OrderQty'].sum()
    big_vwap = (big_part['OrderQty'] * big_part['OrderPrice']).sum() / big_part['OrderQty'].sum()
    res = np.log(big_vwap / sml_vwap) * 1000

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    64 -0.11
    =====>>>> 64.0 -0.11108830998714662 68.08579722286717 155.88343602803343 sss_o_high_price_sell，sss_1s_vols_vwap_buy，zwh_20230921_002，xly_t_trti_pq33，sss_rise1_vwap_a2b，xly_t_trti_pq9 0.7423，0.7385，0.7352，0.7094，0.6722，0.6716
    """
    return pd.Series(factor_dict)