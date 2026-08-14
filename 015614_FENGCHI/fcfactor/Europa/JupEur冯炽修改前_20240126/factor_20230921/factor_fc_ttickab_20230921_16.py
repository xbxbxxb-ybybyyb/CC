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

import decimal
def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                     rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res
def factor_fc_ttickab_20230921_16(df, param_tuple=(), return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0}

    # -----------------------------------------------突破前两分钟买五价与vwap前后端差值对应涨跌幅----------------------------------------------------------
    pre_close = df['pre_close'].iloc[0]
    zt_time = int(df.iloc[-1]['MDTime'])
    df = df[df['MDTime'] >= 93000000]
    df['p2v'] = df['Buy5Price'] - df['WeightedAvgOfferPx']
    df['p2v']=df['p2v'].apply(lambda x:round_(x,6))
    df = df[df['MDTime'] >= max(fun_get_time(zt_time, -120), 93000000)]

    if len(df) > 0:
        res = (df['p2v'][df['p2v'] >round_(df['p2v'].quantile(0.75),6) ].mean() - df[df < round_(df['p2v'].quantile(0.25),6)]['p2v'].mean()) / pre_close
    else:
        res = np.nan
    factor_dict = {factor_name: res}
    #====>>>> 64.08333333333334 -0.10301142677632708 0.014460535288207602 0.05809391997757904 skk_TTickab_px_wb_diff_std，skk_TTickab_h2l_std_b 0.6284，0.6125
    return pd.Series(factor_dict)