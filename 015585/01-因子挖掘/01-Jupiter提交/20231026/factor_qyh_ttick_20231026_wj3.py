import numpy as np
import pandas as pd
# zcz,dtj
# 最后20min里,涨跌幅均值
#
#
factor_name = 'qyh_ttick_20231026_wj3'#
def factor_qyh_ttick_20231026_wj3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.08}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
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
        elif (time1 < 93000000):
            adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
            adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
            return int(adj_tmp_time2_str)
        else:
            return int(tmp_time2_str)
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    if len(tick_df)>0:
        starttime = tick_df['MDTime'].max()
        tick_df['zcz'] = (((tick_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                tick_df.reset_index()['dt'] >= '2020-08-24'))
                                 | (tick_df.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        zcz_flag = tick_df['zcz'].iloc[0]
        if starttime<=93100000:
            sel_trans = tick_df.tail(int(len(tick_df)/3))
        else:
            if starttime>93100000 and starttime<=93500000:
                sec_delta = 30
                endtime = tick_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            elif starttime>93500000 and starttime<=100000000:
                sec_delta = 240
                endtime = tick_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            else:
                sec_delta = 1000
                endtime = tick_df['MDTime'].max()
                starttime = max(fun_get_time(endtime, -sec_delta), 93000000)
            sel_trans = tick_df[(tick_df['MDTime'] > starttime)].copy()
        ret_pct = sel_trans['LastPx'].cummax() / pre_close -1
        if zcz_flag:
            ret_pct = ret_pct/2
        res = (ret_pct - ret_pct.max()).quantile(0.5)
    else:
        res = -0.07
    factor_dict = {factor_name: res}
    return pd.Series(factor_dict)