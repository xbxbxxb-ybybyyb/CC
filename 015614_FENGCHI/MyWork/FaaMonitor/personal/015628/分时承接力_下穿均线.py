# author: kiki_777
# date: 2021/5/31

import sys
sys.path.append('/data/group/800319/RealTime_Data')
from getdata_from_open import *
from datetime import datetime
import sys
sys.path.append('/data/group/800319')
from dataApi.getData import *
from dataApi.stockList import *
from dataApi.tradeDate import *
import requests
import json
import time


def send_message(users, msg):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    for user in users:
        data = {"touser": user,
                "msgtype": "text",
                "agentid": 1000033,
                "text": {"content": msg}}
        json_data = json.dumps(data)
        requests.post(post_url, json_data)


def calc_time_idx(time):
    if time<1300:
        time_idx = (time//100)*60+(time%100)-570
    else:
        time_idx = (time//100)*60+(time%100)-570-90
    return time_idx


today = datetime.today().strftime('%Y%m%d')
daily_data = data_prepare(today)
preclose_day = daily_data['pre_close'].unstack()
limitmax_day = daily_data['max_price'].unstack()
limitmin_day = daily_data['min_price'].unstack()

stock_pool = pd.DataFrame({'股票代码':['000059.SZ', '000301.SZ', '002797.SZ', '600030.SH', '600779.SH'],
                           '证券名称':['华锦股份', '东方盛虹', '第一创业', '中信证券', '水井坊'],
                           '概念板块':['未知', '化工', '券商', '券商', '白酒']}).set_index('股票代码')
stock_list= ['000059.SZ', '000301.SZ', '002797.SZ', '600030.SH', '600779.SH']
trigger_stk = []


def carrying_capacity(stk):

    tmp_df = pd.DataFrame()
    tmp_df['close'] = close[stk]
    tmp_df['avg'] = avgprice[stk]
    tmp_df['above_ave_pct'] = (tmp_df['close']>tmp_df['avg']).cumsum()/(tmp_df['close'] > 0).cumsum()
    tmp_df['close2avg'] = (tmp_df['close']/tmp_df['avg']-1)*100
    tmp_df['cross'] = (tmp_df['close2avg']>0).astype(int).diff()
    tmp_df['pct'] = tmp_df['close'].pct_change(1)
    tmp_df['close_pct'] = tmp_df['close']/preclose_day.loc[today, stk]-1
    tmp_df['avg_pct'] = tmp_df['avg']/preclose_day.loc[today, stk]-1
    tmp_df['close_minus_avg_pct'] = tmp_df['close_pct'] - tmp_df['avg_pct']
    if (abs(tmp_df['close2avg']) >= 0.02).sum()/len(tmp_df) > 0.5 and (abs(tmp_df['close_minus_avg_pct']) >= 0.003).sum()/len(tmp_df) > 0.5 and \
            (tmp_df['cross'] == 1).sum() >= 3 and (tmp_df['cross'] == -1).sum() >= 3:
        tmp_stk_cross = tmp_df[tmp_df['cross'] != 0]
        tmp_stk_downcross = tmp_df[tmp_df['cross'] == -1]
        tmp_stk_upcross = tmp_df[tmp_df['cross'] == 1]
        tmp_interval = tmp_df.loc[(tmp_df.index >= tmp_stk_downcross.index[0]) & (tmp_df.index <= tmp_stk_upcross.index[-1])]
        tmp_stk_cross['time_idx'] = tmp_stk_cross.index.map(calc_time_idx)
        tmp_stk_cross['interval'] = tmp_stk_cross['time_idx'].diff()
        abv_avg_longest = tmp_stk_cross.loc[tmp_stk_cross['cross'] == -1, 'interval'].max()
        abv_avg_longest_time = tmp_stk_cross.loc[tmp_stk_cross['cross'] == -1, 'interval'].argmax()
        be_avg1 = tmp_stk_cross.loc[(tmp_stk_cross['cross'] == 1) & (tmp_stk_cross.index < abv_avg_longest_time), 'interval'].max()
        if (abs(tmp_interval['close2avg']) >= 0.003).sum() / tmp_interval.shape[0] <= 0.5:
            pass
        elif tmp_df['avg'].tolist()[-1] < tmp_df.loc[945, 'avg']:
            pass
        elif (abs(tmp_interval['close_minus_avg_pct']) >= 0.02).sum() / tmp_interval.shape[0] <= 0.5:
            pass
        elif tmp_df['close'].max() / tmp_df['avg'].tolist()[-1] - 1 >= 0.05 if int(stk[:6]) // 100 == 300 else 0.03:
            pass
        elif (abv_avg_longest > 60) & (be_avg1 > 15) & (tmp_df['close'].tolist()[-1] < tmp_df['avg'].tolist()[-1]):
            pass
        else:
            low_dict = {'time': [], 'low_point': [], 'downcross_time': [], 'upcross_time': [], 'pre_high': [], 'largest_dis_to_avg': []}
            for i in range(1, tmp_stk_upcross.shape[0]):
                if tmp_stk_upcross.index[i] <= 945:
                    pass
                elif tmp_stk_cross.loc[tmp_stk_cross.index < tmp_stk_upcross.index[i - 1]].empty:
                    pass
                elif tmp_stk_cross.loc[tmp_stk_cross.index < tmp_stk_upcross.index[i]].empty:
                    pass
                else:
                    interval_df = tmp_df.loc[(tmp_df.index <= tmp_stk_upcross.index[i]) & (tmp_df.index >= tmp_stk_cross.loc[tmp_stk_cross.index < tmp_stk_upcross.index[i]].index[-1])]
                    interval_df2 = tmp_df.loc[(tmp_df.index < interval_df.index[0]) & (tmp_df.index >= tmp_stk_cross.loc[tmp_stk_cross.index < tmp_stk_upcross.index[i - 1]].index[-1])]
                    low_value = interval_df['close'].min()
                    low_point = interval_df['close'].argmin()
                    pre_high_value = interval_df2['close'].max()
                    pre_high_point = interval_df2['close'].argmax()
                    low_dict['time'].append(low_point)
                    low_dict['low_point'].append(low_value)
                    low_dict['upcross_time'].append(interval_df.index[-1])
                    low_dict['downcross_time'].append(interval_df.index[0])
                    low_dict['pre_high'].append(pre_high_value)
                    largest_dist = abs(tmp_df.loc[(tmp_df.index >= pre_high_point) & (tmp_df.index <= low_point), 'close2avg']).max()
                    low_dict['largest_dis_to_avg'].append(largest_dist)
            low_df = pd.DataFrame(low_dict)
            low_df['idx'] = low_df['time'].apply(calc_time_idx)
            low_df = low_df.set_index('time')
            low_df['close2avg'] = tmp_df.loc[low_df.index, 'close2avg']
            low_df['distance_rank'] = low_df['close2avg'].rank()
            low_df['interval_time'] = low_df['upcross_time'].apply(calc_time_idx) - low_df['downcross_time'].apply(calc_time_idx)
            low_df = low_df.sort_values('distance_rank')
            low_df = low_df[low_df['largest_dis_to_avg'] > 0.003]
            if (low_df['interval_time'] >= 60).sum() > 0:
                pass
            elif low_df.shape[0] < 3:
                pass
            else:
                filtered_low = {'time': [], 'idx': [], 'low_point': [], 'close2avg': [], 'left_high': [], 'right_high': [], 'cross_time': []}
                filtered_low['time'].append(low_df.index[0])
                filtered_low['idx'].append(low_df['idx'].iloc[0])
                filtered_low['low_point'].append(low_df['low_point'].iloc[0])
                filtered_low['close2avg'].append(low_df['close2avg'].iloc[0])
                filtered_low['left_high'].append(tmp_df.loc[(tmp_df.index < low_df.index[0])].iloc[-5:, :]['close'].max())
                filtered_low['right_high'].append(tmp_df.loc[(tmp_df.index > low_df.index[0])].iloc[0:5, :]['close'].max())
                filtered_low['cross_time'].append(tmp_stk_cross.loc[(tmp_stk_cross.index > low_df.index[0]) & (tmp_stk_cross['cross'] == 1)].index[0])
                i = 1
                while i <= low_df.index.shape[0] - 1:
                    if abs(low_df['idx'].iloc[i] - filtered_low['idx']).min() < 10:
                        i += 1
                    else:
                        filtered_low['time'].append(low_df.index[i])
                        filtered_low['idx'].append(low_df['idx'].iloc[i])
                        filtered_low['low_point'].append(low_df['low_point'].iloc[i])
                        filtered_low['close2avg'].append(low_df['close2avg'].iloc[i])
                        filtered_low['left_high'].append(tmp_df.loc[(tmp_df.index < low_df.index[i])].iloc[-5:, :]['close'].max())
                        filtered_low['right_high'].append(tmp_df.loc[(tmp_df.index > low_df.index[i])].iloc[0:5, :]['close'].max())
                        filtered_low['cross_time'].append(tmp_stk_cross.loc[(tmp_stk_cross.index > low_df.index[i]) & (tmp_stk_cross['cross'] == 1)].index[0])
                        i += 1
                filtered_low_df = pd.DataFrame(filtered_low)
                filtered_low_df['cross_time_idx'] = filtered_low_df['cross_time'].apply(calc_time_idx)
                filtered_low_df['interval_time'] = filtered_low_df['cross_time_idx'] - filtered_low_df['idx']
                filtered_low_df['recover_ratio'] = (filtered_low_df['right_high'] / filtered_low_df['low_point'] - 1) / (filtered_low_df['left_high'] / filtered_low_df['low_point'] - 1)
                filtered_low_df.columns = ['时间', '时间序列号', '低点', '低点与均线距离', '低点左侧5min高点','低点右侧5min高点', '低点后上穿时间', '上穿时间序列号', '低点后上穿时间间隔','反弹幅度']
                if filtered_low_df.shape[0] < 3:
                    pass
                elif (filtered_low_df['反弹幅度'] >= 0.6).sum() < 2:
                    pass
                elif (filtered_low_df['低点后上穿时间间隔'] <= 25).sum() < filtered_low_df.shape[0]:
                    pass
                else:
                    send_message(['015628','011669'], '%s, %s板块内%s价格在均线上方且出现分时承接' %
                                 (datetime.now().strftime('%H:%M:%S'), stock_pool.loc[stk, '概念板块'],
                                  stock_pool.loc[stk, '证券名称']))


while 15 > time.localtime()[3] >= 10:

    stock_data = get_stock_factor(['ClosePx', 'HighPx', 'TotalVolumeTrade', 'TotalValueTrade', 'MeanPrice'], stock_list)
    close = stock_data['ClosePx']
    pct_1m = close / close.shift(1) - 1
    high = stock_data['HighPx']
    cumhigh = high.expanding().max()
    volume = stock_data['TotalVolumeTrade']
    amt = stock_data['TotalValueTrade']
    avgprice = stock_data['MeanPrice']

    for code in stock_list:
        carrying_capacity(code)

    stock_list = list(set(stock_list)-set(trigger_stk))

