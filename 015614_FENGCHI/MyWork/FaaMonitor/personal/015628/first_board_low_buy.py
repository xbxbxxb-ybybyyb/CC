# author: kiki_777
# date: 2021/6/3

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
pre_date = str(get_pre_trade_date(int(today), 1))
daily_data = data_prepare(today)
preclose_day = daily_data['pre_close'].unstack()
limitmax_day = daily_data['max_price'].unstack()
limitmin_day = daily_data['min_price'].unstack()


def get_daily_factor(factor_name):

    date_range = get_date_range(get_pre_trade_date(int(today), 150), get_pre_trade_date(int(today), 0))
    factor_df = get_daily_1factor(factor_name, date_range)
    factor_df.index = factor_df.index.map(str)
    factor_df.columns = factor_df.columns.map(trans_int2windcode)

    return factor_df


def interday_condition():

    close_badj = get_daily_factor('close_badj')
    ma5 = close_badj.rolling(5).mean()
    ma20 = close_badj.rolling(20).mean()
    ma60 = close_badj.rolling(60).mean()
    vol = get_daily_factor('volume')
    vol_ratio = vol / vol.shift(1)
    zt = get_daily_factor('limit_up')
    zt_3d = zt.rolling(3).sum().shift(1)
    pct = get_daily_factor('pct_chg')

    result = (vol_ratio > 2) & (zt == 1) & (zt_3d == 0) & (pct > 9) & (~((ma5 < ma20) & (ma20 < ma60))).shift(1)

    return result


f = interday_condition()

stock_list = f.loc[pre_date][f.loc[pre_date] == 1].index.tolist()


