import sys
import requests
import json

sys.path.append('/data/group/800442/800319/')
from dataApi.stockList import _store_ST, _store_limit_range
from basicUpdate.daily import *

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


update_stock_list(address='/data/group/800442/800319/junkData/daily')
update_ind_con(address='/data/group/800442/800319/junkData/daily')
for i in range(len(daily_data_list)):
    try:
        update_daily_data(daily_data_list[i], address='/data/group/800442/800319/junkData/daily')
    except Exception:
        if dt.datetime.now().hour < 18:
            print(daily_data_list[i])
        else:
            print(daily_data_list[i])
#            raise Exception
update_pause(address='/data/group/800442/800319/junkData/daily')
update_live_days(address='/data/group/800442/800319/junkData/daily')
update_normal_days(address='/data/group/800442/800319/junkData/daily')
update_price_get_limit(address='/data/group/800442/800319/junkData/daily')
update_dividend(address='/data/group/800442/800319/junkData/daily')
_store_ST(address='/data/group/800442/800319/junkData/daily')
_store_limit_range(address='/data/group/800442/800319/junkData/daily')
amend_daily_data(address='/data/group/800442/800319/junkData/daily')
send_message(['016385','011669', '015624', '015614'], 'daily data updated')
