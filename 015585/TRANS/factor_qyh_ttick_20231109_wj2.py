import pandas as pd
import datetime as dt
import numpy as np
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
    elif (time1 < 93000000):
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)
def factor_qyh_ttick_20231109_wj2(transaction_df, return_fillna_dic=False):
    factor_name = 'qyh_ttick_20231109_wj2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    transaction_df['VolumeTrade'] = transaction_df['TotalVolumeTrade'].diff()
    transaction_df['ValueTrade'] = transaction_df['TotalValueTrade'].diff()
    if len(transaction_df) > 0:
        starttime = transaction_df['MDTime'].max()
        if starttime <= 93100000:
            sel_trans_before = transaction_df.tail(int(2 * len(transaction_df) / 3))
        else:
            if starttime > 93100000 and starttime <= 93500000:
                sec_delta = 40
                endtime = transaction_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            elif starttime > 93500000 and starttime <= 100000000:
                sec_delta = 240
                endtime = transaction_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            else:
                sec_delta = 1200
                endtime = transaction_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)

            sel_trans_before = transaction_df[(transaction_df['MDTime'] >= starttime)].copy()
        ret_pct_b = ((sel_trans_before['HighPx']) - sel_trans_before['pre_close']) \
                    / (sel_trans_before['LastPx'] + 1e-3)
        ret = (ret_pct_b.quantile(0.7))
    else:
        ret = 0
    factor_dict = {factor_name: ret}
    return pd.Series(factor_dict)