# @Time : 2021/2/22 13:58
# @Author : Zhichen Lu
# @File : period_info_update.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')

from dataApi.tradeDate import get_date_range, get_pre_trade_date
import configparser
import os

import datetime
import requests, json

local_config_path = '/data/group/800319/strategy_local_path_offline/'
if not os.path.exists(local_config_path):
    os.mkdir(local_config_path)


def send_message(users, msg):
    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    if isinstance(users, list):
        users = '|'.join(users)

    data = {"touser": users,
            "msgtype": "text",
            "agentid": 1000033,
            "text": {"content": msg}}
    json_data = json.dumps(data)
    requests.post(post_url, json_data)


def get_rolling_index(start, end, period=10, period_predict=10):
    date_list = get_date_range(start, end)
    rolling_train_test_idx_list = []
    if len(date_list) == period:
        return [(0, (date_list[0], date_list[-1], date_list[-1], date_list[-1]))]
    else:
        length = (len(date_list) - period) // period_predict + 1
    for idx in range(length):
        train_start_idx = idx * period_predict
        train_end_idx = idx * period_predict + period - 1
        if idx == (len(date_list) - period) // period_predict:
            if (len(date_list) - period) % period_predict == 0:
                test_end_idx, test_start_idx = len(date_list) - 1, len(date_list) - 1
            else:
                test_start_idx = idx * period_predict + period
                test_end_idx = len(date_list) - 1
        else:
            test_start_idx = idx * period_predict + period
            test_end_idx = test_start_idx + period_predict - 1
        train_start_date, train_end_date, test_start_date, test_end_date = [date_list[i] for i in
                                                                            [train_start_idx, train_end_idx,
                                                                             test_start_idx, test_end_idx]]
        rolling_train_test_idx_list.append(
            (idx, (train_start_date, train_end_date, test_start_date, test_end_date)))
    return rolling_train_test_idx_list

period_info = get_rolling_index(20190313, 20210526, 200, 350)

conf = configparser.ConfigParser()
conf['period_info'] = {'period_info': period_info}

if os.path.exists(local_config_path + 'period_info_20200102_model.ini'):
    os.remove(local_config_path + 'period_info_20200102_model.ini')
with open(local_config_path + 'period_info_20200102_model.ini', 'w') as configfile:
    conf.write(configfile)



"""
try:
    start = 20150309
    end = int(datetime.date.today().strftime('%Y%m%d'))
    period_info = get_rolling_index(start, 20210525, 200, 10) + get_rolling_index(20200728,end,200,1)
    print(period_info)
    _, last_cell = period_info[-1]
    if last_cell[1] == last_cell[2] and last_cell[2] == last_cell[3]:
        pass
    else:
        period_info = get_rolling_index(start, get_pre_trade_date(end), 200, 10)

    conf = configparser.ConfigParser()
    conf['period_info'] = {'period_info': period_info}

    if os.path.exists(local_config_path + 'period_info.ini'):
        os.remove(local_config_path + 'period_info.ini')
    with open(local_config_path + 'period_info.ini', 'w') as configfile:
        conf.write(configfile)
    if period_info[-1][1][-1]==period_info[-1][1][-2] and period_info[-1][1][-1]==end:
        send_message(['015664','016385'],'Today is a big day')
    send_message(['015664'], 'period_info_update Done---------------------')
except:
    send_message(['015664'], 'period_info_update Wrong!!!!!!!!!!!!!!!!!!!!')

"""

