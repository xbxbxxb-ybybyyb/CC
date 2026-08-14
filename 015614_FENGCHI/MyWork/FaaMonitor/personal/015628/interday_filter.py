# author: kiki_777
# date: 2021/6/1

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
date_range = get_date_range(get_pre_trade_date(int(today), 60), get_pre_trade_date(int(today), 1))


def cross_star():

    close = get_daily_1factor('close_badj', date_list=date_range)
    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()

    dt = (ma5 > ma10) & (ma5 > ma20)
