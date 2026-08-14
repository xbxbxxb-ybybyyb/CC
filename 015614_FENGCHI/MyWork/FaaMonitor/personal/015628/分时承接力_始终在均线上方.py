# author: kiki_777
# date: 2021/5/28

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
    tmp_df['dis_to_ave'] = (tmp_df['close']/tmp_df['avg']-1)*100
    tmp_df['cross'] = (tmp_df['dis_to_ave']>0).astype(int).diff()
    tmp_df['pct'] = tmp_df['close'].pct_change(1)
    tmp_df['close_pct'] = tmp_df['close']/preclose_day.loc[today, stk]-1
    tmp_df['avg_pct'] = tmp_df['avg']/preclose_day.loc[today, stk]-1
    tmp_df['close_minus_avg_pct'] = tmp_df['close_pct'] - tmp_df['avg_pct']

    # 1.判断在均线上方时间占比是否>50%
    if tmp_df['above_ave_pct'].tolist()[-1] < 0.5:
        pass
    # 2.判断9:45之后是否一直在均线上方
    elif (tmp_df.loc[945:, 'cross'] == -1).sum() > 0:
        pass
    elif (tmp_df.loc[945:, 'cross'] == 1).sum() > 1:
        pass
    # 3.判断9:45之后距离均线最近的3个点附近的承接力情况
    else:
        tmp_df['low_point'] = (tmp_df['close'] < tmp_df['close'].shift(1)) & (tmp_df['close'] < tmp_df['close'].shift(-1))
        tmp_df['high_point'] = (tmp_df['close'] > tmp_df['close'].shift(1)) & (tmp_df['close'] > tmp_df['close'].shift(-1))
        tmp_df['dis_to_ave_rank'] = tmp_df[(tmp_df['low_point'] == 1) & (tmp_df.index >= 945) & (tmp_df['close_minus_avg_pct'] <= 0.03)]['dis_to_ave'].rank()
        three_point_df = tmp_df[tmp_df['dis_to_ave_rank'] <= 3]
        if three_point_df.shape[0] < 3:
            pass
        else:
            extreme_dict = {'low': [], 'low_time': [], 'left_high': [], 'right_high': []}
            for i in range(three_point_df.shape[0]):
                t1 = three_point_df.index[i]
                low_point = three_point_df['close'].iloc[i]
                low_time = t1
                high1 = tmp_df.loc[(tmp_df.index < low_time)].iloc[-5:, :]['close'].max()
                high2 = tmp_df.loc[(tmp_df.index > low_time)].iloc[0:5, :]['close'].max()
                extreme_dict['low'].append(low_point)
                extreme_dict['low_time'].append(low_time)
                extreme_dict['left_high'].append(high1)
                extreme_dict['right_high'].append(high2)
            extreme_df = pd.DataFrame(extreme_dict)
            extreme_df['down_pct'] = abs(extreme_df['low'] / extreme_df['left_high'] - 1)
            extreme_df['up_pct'] = abs(extreme_df['right_high'] / extreme_df['low'] - 1)
            extreme_df['recover_ratio'] = extreme_df['up_pct'] / extreme_df['down_pct']
            extreme_df['recover_score'] = [10 if x >= 1 else x * 10 for x in extreme_df['recover_ratio']]
            if (extreme_df[extreme_df['recover_score'] >= 6].shape[0] >= 2) & (extreme_df['recover_score'].sum() >= 15):
                send_message(['015628', '011669'], '%s, %s板块内%s价格在均线上方且出现分时承接' % (datetime.now().strftime('%H:%M:%S'),
                                                                                  stock_pool.loc[stk, '概念板块'],
                                                                                  stock_pool.loc[stk, '证券名称']))
                trigger_stk.append(stk)
            else:
                pass


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
    time.sleep(1)



