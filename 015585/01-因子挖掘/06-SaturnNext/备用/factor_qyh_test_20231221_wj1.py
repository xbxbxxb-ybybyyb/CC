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
import decimal
def round_(x, n=0):
    if n>0:
        res=float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1'%('0'*(n-1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res=int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res


def factor_qyh_test_20231221_wj1(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_test_20231221_wj1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'].diff()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'].diff()
    pre_close = tick_df['pre_close'].iloc[0]
    close = tick_df['LastPx'].iloc[-1]
    high_px = tick_df['LastPx'].max()
    low_px = tick_df['LowPx'].min()
    if high_px > pre_close:
        compare_pc = pre_close
        zt_timelist = tick_df[tick_df['LastPx'] >= compare_pc].MDTime.tolist()
        last_high_time = np.max(zt_timelist)
    else:
        zt_timelist = tick_df[tick_df['LastPx'] >= high_px].MDTime.tolist()
        last_high_time = fun_get_time(np.max(zt_timelist), 900)
    if len(tick_df) > 0:
        sec_delta = 900
        starttime = max(fun_get_time(last_high_time, -sec_delta), 93000000)
        sel_trans_before = tick_df[
            (tick_df['MDTime'] <= last_high_time) & (tick_df['MDTime'] >= starttime)]
        ret_pct_b = (sel_trans_before['LastPx'] - low_px) / pre_close
        ret = ret_pct_b.max()
    else:
        ret = 0
    factor_dict = {factor_name: ret}
    return pd.Series(factor_dict)