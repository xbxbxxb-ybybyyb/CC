import sys
import requests
import json
sys.path.append('/data/user/015614/Lucien')

from dataApi.stockList import _store_ST, _store_limit_range
from DailyDataUpdate.basicUpdate.daily import *
from dataApi.sendInfo import send_message

# def send_message(users, msg):
#
#     token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
#                  'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
#     send_url = " http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
#     con = requests.get(token_url)
#     json_text = json.loads(con.text)
#     access_token = json_text["access_token"]
#     post_url = send_url.format(access_token)
#
#     for user in users:
#         data = {"touser": user,
#                 "msgtype": "text",
#                 "agentid": 1000033,
#                 "text": {"content": msg}}
#         json_data = json.dumps(data)
#         requests.post(post_url, json_data)


update_stock_list(address='/data/user/015614/easy_transfer/basic_data/daily')
update_ind_con(address='/data/user/015614/easy_transfer/basic_data/daily')
for i in range(len(daily_data_list)):
    try:
        update_daily_data(daily_data_list[i], address='/data/user/015614/easy_transfer/basic_data/daily')
    except Exception:
        if dt.datetime.now().hour < 18:
            print(daily_data_list[i])
        else:
            print(daily_data_list[i])
#            raise Exception
update_pause(address='/data/user/015614/easy_transfer/basic_data/daily')
update_live_days(address='/data/user/015614/easy_transfer/basic_data/daily')
update_normal_days(address='/data/user/015614/easy_transfer/basic_data/daily')
update_price_get_limit(address='/data/user/015614/easy_transfer/basic_data/daily')
update_dividend(address='/data/user/015614/easy_transfer/basic_data/daily')
_store_ST(address='/data/user/015614/easy_transfer/basic_data/daily')
_store_limit_range(address='/data/user/015614/easy_transfer/basic_data/daily')
amend_daily_data(address='/data/user/015614/easy_transfer/basic_data/daily')
send_message('日频基础数据均以更新')
