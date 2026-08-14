
# coding: utf-8
# Author：fengchi863
# Date ：2023/9/6 14:00

import datetime as dt

import numpy as np
import pandas as pd


def fun_get_time(time1, sec_delta):
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

# import pandas as pd
# check= pd.read_hdf('/data/user/015614/factor/dig_Trans_TOrder2_20230925105412/(8, 180).h5')
# check.quantile(0.95)

def factor_fc_trans_order_20230928_12(df, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]
    if return_fillna_dic:
        return {factor_name: 0.0}
    # ----------------------------------------------------突破前近10秒相对于过去3分钟内卖出委托量中成交量的比值-------------------------------------------------------------
    dt, Ticker = df.index[0]
    pre_close = df['pre_close'].iloc[0]
    zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')
    ul_price = np.floor(pre_close * 1.1 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 1.2 * 100 + 0.5 + 1e-8) / 100
    dt_price = np.floor(pre_close * 0.9 * 100 + 0.5 + 1e-8) / 100 if not zcz else np.floor(pre_close * 0.8 * 100 + 0.5 + 1e-8) / 100
    zt_time = df['MDTime'].max()

    trans_df = df.query('type == 0')[['MDTime', 'TradeBuyNo', 'TradeSellNo', 'TradePrice', 'TradeQty', 'TradeMoney']].copy()
    trans_df = trans_df.query('MDTime >= 93000000 & TradePrice > 0')
    trans_df['m'] = trans_df['MDTime'] // 100000
    trans_df = trans_df[trans_df['TradeMoney'] > 0]
    trans_df['buy_flag'] = (trans_df['TradeBuyNo'] > trans_df['TradeSellNo']) * 1.0

    order_df = df.query('type == 1')[['MDTime', 'OrderIndex', 'OrderType', 'OrderPrice', 'OrderQty', 'OrderBSFlag']].copy()
    order_df = order_df.query('MDTime >= 93000000')
    order_df['m'] = order_df['MDTime'] // 100000
    order_df = order_df[order_df['OrderBSFlag'].isin([1, 2])]
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 1), 'OrderPrice'] = ul_price
    order_df.loc[(order_df['OrderType'] == 1) & (order_df['OrderBSFlag'] == 2), 'OrderPrice'] = dt_price
    order_df = order_df.query(f'{dt_price} <= OrderPrice <= {ul_price}')
    order_df['OrderMoney'] = order_df['OrderPrice'] * order_df['OrderQty']

    short_time = 8
    mid_time = 180
    target_time1 = max(fun_get_time(zt_time, -short_time), 93000000)
    target_time2 = max(fun_get_time(zt_time, -mid_time), 93000000)

    order_df = order_df.query(f'OrderBSFlag == 2')
    part_order_df1 = order_df.query(f'MDTime >= {target_time1}')
    part_trans_df1 = trans_df.query(f'MDTime >= {target_time1}')
    part_order_df2 = order_df.query(f'{target_time1} >= MDTime >= {target_time2}')
    part_trans_df2 = trans_df.query(f'{target_time1} >= MDTime >= {target_time2}')

    factor1 = part_trans_df1['TradeQty'].sum() / part_order_df1['OrderQty'].sum(min_count=1)
    factor2 = part_trans_df2['TradeQty'].sum() / part_order_df2['OrderQty'].sum(min_count=1)

    if np.isnan(factor1): factor1 = 0
    if np.isnan(factor2): factor2 = 0

    factor = factor1 / (factor2 + 0.001)
    factor = 0 if factor > 250 else factor
    factor_dict = {factor_name: factor}
    """
    72.625 0.108
    =====>>>> 73.875 0.11640435085067702 10.607784227233271 24.721009413673908 sss_to_rawratio_sell_s30s60，t_l1_trade_ave_time 0.6284，0.6216
    """
    return pd.Series(factor_dict)