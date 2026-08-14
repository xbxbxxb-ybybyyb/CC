import numpy as np
import pandas as pd
import datetime as dt
# zcz,dtj
#
#
#
factor_name = 'qyh_ttick_20231130_wj'#
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

def factor_qyh_ttick_20231130_wj(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tickdata = transaction_df[transaction_df['type'] == 1]
    orderdata = transaction_df[transaction_df['type'] == 0]
    tickdata = tickdata[tickdata['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    orderdata = orderdata[orderdata['MDTime'] >= 93000000]
    orderdata = orderdata[orderdata['OrderType'] != 1]  # 选择连续竞价阶段的逐笔成交数据
    if len(orderdata) > 0:
        orderdata['zcz'] = (((orderdata.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                orderdata.reset_index()['dt'] >= '2020-08-24'))
                            | (orderdata.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
        zcz_flag = orderdata['zcz'].iloc[0]
        pre_close = orderdata['pre_close'].iloc[0]
        starttime = orderdata['MDTime'].max()

        sel_tick_before = tickdata[(tickdata['MDTime'] >= 93000000)]
        sel_order_before = orderdata[(orderdata['MDTime'] >= 93000000)]

        sel_order_before = sel_order_before[sel_order_before['OrderBSFlag'] == 2]
        sorderpx = (sel_order_before['OrderPrice'] * sel_order_before['OrderQty'] * sel_order_before['OrderPrice']).sum()/ \
                   (sel_order_before['OrderQty']*sel_order_before['OrderPrice']).sum()
        ret = ((sel_tick_before['WeightedAvgOfferPx'] - sorderpx) / pre_close)
        ret = ret.std()
        if zcz_flag:
            ret = ret / 2
    else:
        ret = 0

    factor_dict = {factor_name: ret}
    return pd.Series(factor_dict)