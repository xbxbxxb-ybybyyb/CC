import numpy as np
import pandas as pd
# zcz,dtj
# 最后20min里,涨跌幅均值，测试66分的因子代码
#
#
# -*- coding: utf-8 -*-
import pandas as pd
from xquant.factordata import FactorData
s = FactorData()
import datetime as dt
def fun_get_time(time1,sec_delta):
    #计算给定时间戳time1在sec_delta秒后的时间戳
    tmp_time = dt.datetime.strptime(str(time1)[:-3],'%H%M%S')
    tmp_time2 = tmp_time+dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
    if (int(tmp_time2_str)>113000000)&(time1<=113000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<130000000)&(time1>=130000000):
        adj_tmp_time2 = tmp_time2-dt.timedelta(seconds=1.5*3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str)<93000000)&(time1>=93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif (time1<93000000):
        adj_tmp_time2 = tmp_time2+dt.timedelta(seconds=4*60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S')+str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)
import decimal
def round_(x, n=0):
    if n>0:
        res=float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1'%('0'*(n-1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res=int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

def factor_qyh_ttick_20231026_wj4(transaction_df, return_fillna_dic=False):
    factor_name = 'qyh_ttick_20231026_wj4'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.07}
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    transaction_df['VolumeTrade'] = transaction_df['TotalVolumeTrade'].diff()
    transaction_df['ValueTrade'] = transaction_df['TotalValueTrade'].diff()
    vol_med = float(transaction_df['ValueTrade'].quantile(0.75))
    vol_min = round_(vol_med, 4)
    transaction_df = transaction_df[(transaction_df['ValueTrade'] >= vol_min)]
    if len(transaction_df)>0:
        starttime = transaction_df['MDTime'].max()
        transaction_df['zcz'] = (((transaction_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                transaction_df.reset_index()['dt'] >= '2020-08-24'))
                                 | (transaction_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        zcz_flag = transaction_df['zcz'].iloc[0]
        if starttime<=93100000:
            sel_trans = transaction_df.tail(int(len(transaction_df)/2))
        else:
            if starttime>93100000 and starttime<=93500000:
                sec_delta = 40
                endtime = transaction_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            elif starttime>93500000 and starttime<=100000000:
                sec_delta = 240
                endtime = transaction_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            else:
                sec_delta = 1200
                endtime = transaction_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            sel_trans = transaction_df[(transaction_df['MDTime'] > starttime)].copy()

        ret_pct = (sel_trans['LastPx'].cummax() - sel_trans['pre_close'] + 1e-2) / (
                    sel_trans['pre_close'] + 1e-2)

        if zcz_flag:
            ret_pct = ret_pct/2
        ret = (ret_pct - ret_pct.max()).median()

    else:
        ret = -0.07
    factor_dict = {factor_name: ret}
    return pd.Series(factor_dict)