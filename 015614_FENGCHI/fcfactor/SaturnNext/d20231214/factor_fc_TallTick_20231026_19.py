# coding: utf-8
# Author：fengchi863
# Date ：2023/5/10 21:13

import pandas as pd
import numpy as np
import datetime as dt
import decimal
def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

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

def factor_fc_TallTick_20231026_19(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    # ---------------------------------------------突破前1分钟内Tick区间涨跌幅大于1%所占比例增长绝对值---------------------------------------------------------
    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
    ZT_Time = df['MDTime'].max()
    pre_close = df['pre_close'].iloc[0]
    df = df[df['MDTime'] >= 93000000]

    df['itvl_pct'] = ((df['LastPx'] - df['LastPx'].shift(20)) / pre_close).apply(lambda x: round_(x, 4))
    if zcz: df['itvl_pct'] /= 2

    if len(df) <= 20:
        res = 0
    else:
        df_head = df.head(df.shape[0] - 20)
        res1 = df_head.query(f'itvl_pct >= 0.01').shape[0] / df_head.shape[0]
        df_tail = df.tail(20)
        res2 = df_tail.query(f'itvl_pct >= 0.01').shape[0] / df_tail.shape[0]
        res = res2 - res1

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    """
    55.83 -0.10981
    =====>>>> 55.833333333333336 -0.10981264773728157 0.33274729080121473 0.3713473946572207 fc_ttickab_20230921_16，xbc_20230831_9 0.688，0.6706
    !!!! fc_ttickab_20231026_15 0.6989307568955345
    !!!! fc_ttickab_20231026_18 0.6989307568955345
    eur2mimas:
    22.125 0.06392
    =====>>>> 22.125 0.06392251481614311 -0.011662625074688453 0.05879368130205643 skk_hc2l，qyh_m5_pnorm_3 0.6721，0.6654
    !!!! fc_TallTick_20231026_15 0.7381636451045045
    """
    return pd.Series(factor_dict)