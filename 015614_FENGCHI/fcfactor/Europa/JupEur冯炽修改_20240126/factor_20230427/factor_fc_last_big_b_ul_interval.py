# coding: utf-8
# Author：fengchi863
# Date ：2023/4/27 15:47

import pandas as pd
import numpy as np
import datetime as dt

def factor_fc_last_big_b_ul_interval(df, return_fillna_dic=False):
    factor_name = 'fc_last_big_b_ul_interval'

    if return_fillna_dic:
        return {factor_name: 0}

    dt, Ticker = df.index[0]
    ff_shares = df['ff_shares'].iloc[0]
    df = df[df['TradeMoney'] > 0]
    df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(float)
    df = df[df['MDTime'] >= 93000000]

    sell_df = df[df['buy_flag'] == 0]
    group_sell_df = sell_df.groupby('TradeSellNo').agg({'TradeMoney': sum,
                                                        'TradeIndex': min})  # 保留大户
    big_group_sell = group_sell_df.query(f'TradeMoney > 200000')
    last_index = big_group_sell['TradeIndex'].iloc[-1] if len(big_group_sell) > 0 else 0

    # 最后一笔卖单下单时到现在的时间长度
    if len(big_group_sell) > 0:
        last_sell_mdtime = df.query(f'TradeIndex == {last_index}').iloc[0]['MDTime']
        first_ul_mdtime = df.query(f'TradePrice == {df["TradePrice"].max()}').iloc[0]['MDTime']

        last_sell_mdtime_dt = dt.strptime(str(int(last_sell_mdtime)), '%H%M%S%f')
        first_ul_mdtime_dt = dt.strptime(str(int(first_ul_mdtime)), '%H%M%S%f')

        if last_sell_mdtime_dt > first_ul_mdtime_dt:
            ret = 0
        else:
            time_delta = first_ul_mdtime_dt - last_sell_mdtime_dt
            ret = time_delta.seconds + time_delta.microseconds / 1000000
            if first_ul_mdtime > 120000000 > last_sell_mdtime:
                ret -= 5400
    else:
        ret = 0.0001

    factor_dict = {factor_name: np.log(1 + ret)}

    return pd.Series(factor_dict)