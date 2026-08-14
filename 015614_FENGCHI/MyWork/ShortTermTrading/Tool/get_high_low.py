# coding: utf-8
# Author：fengchi863
# Date ：2020/9/29 10:25

'''
采用高低点的方式计算大盘的高低点，从而统计当前时间上的跌幅和跌速
'''

import pandas as pd

from ShortTermTrading.dataApi.getData import get_minute_1stock

fast = 'ma5'
slow = 'ma10'


def is_fast_slow(fast, slow):
    if fast >= slow:
        return 1
    else:
        return 0


def peaks(stk_minute_data, first, second, direct, point_dict):
    if direct == 'Low':
        low_value = stk_minute_data.loc[first:second, 'low'].min()
        loc_time = stk_minute_data.loc[first:second, 'low'].idxmin()
        point_dict['down_peaks']['loc_time'].append(loc_time)
        point_dict['down_peaks']['low'].append(low_value)
    elif direct == 'High':
        high_value = stk_minute_data.loc[first:second, 'low'].max()
        loc_time = stk_minute_data.loc[first:second, 'low'].idxmax()
        point_dict['up_peaks']['loc_time'].append(loc_time)
        point_dict['up_peaks']['high'].append(high_value)
    else:
        pass


def get_high_low(stk_minute_data):
    point_dict = {'up_peaks': {'loc_time': [], 'high': []},
                  'down_peaks': {'loc_time': [], 'low': []}}
    stk_minute_data[fast] = stk_minute_data['open'].rolling(window=5).mean()
    stk_minute_data[slow] = stk_minute_data['open'].rolling(window=10).mean()
    stk_minute_data['diff_ma'] = stk_minute_data[[fast, slow]].apply(lambda x: is_fast_slow(x[fast], x[slow]),
                                                                     axis=1, raw=False).diff()
    point_data = stk_minute_data[stk_minute_data['diff_ma'] != 0]['diff_ma']
    for i in range(1, len(point_data)):
        if i == 1:
            first_time = point_data.index[0]
            second_time = point_data.index[1]
            if point_data.iloc[i] == 1:
                direction = 'Low'
            else:
                direction = 'High'
        elif i == len(point_data):
            first_time = point_data.index[i]
            second_time = stk_minute_data.index[len(point_data)]
            if point_data.iloc[i] == 1:
                direction = 'High'
            else:
                direction = 'Low'
        else:
            first_time = point_data.index[i - 1]
            second_time = point_data.index[i]
            if point_data.iloc[i] == 1:
                direction = 'Low'
            else:
                direction = 'High'
        peaks(stk_minute_data, first_time, second_time, direction, point_dict)
    return point_dict


start_date = 20200901
end_date = 20200920
start_datetime = start_date * 10000 + 930
end_datetime = end_date * 10000 + 1500
mkt_minute_open = get_minute_1stock('SZZZ', factor_list=['open', 'high', 'low', 'close'], type='bench').loc[
                  (start_date, 930):(end_date, 1500), :]
mkt_minute_open.index.name = 'date', 'time'
point_dict = get_high_low(mkt_minute_open.loc[(20200907, slice(None)), :])

aa = pd.DataFrame(point_dict)
# aa.to_excel('/data/group/800319/fengchi/junxian.xlsx')
