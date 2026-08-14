import os
from LimitUpPredStrategy.Factor.FactorTest import FactorTest
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
factor_list = os.listdir('/data/group/800442/800319/ZTfactors/Untested/')
zxf_factors = [x[:-4] for x in factor_list if 'zxfalgo' in x]
zxf_factors.sort(reverse=True)
approve_list = []
self = FactorTest(start_date=20140101,
                      backtest_start_date=20140701, end_date=20191231,
                      stock_pool_address='/data/group/800442/800319/LimitUpStrategy/FilteredTick.pkl')
for factor in zxf_factors:
    print(factor)
    flag = self.factor_test(factor)
    if flag is True:
        approve_list.append(factor)
        send_message(['015630'],'%s新标准入库'%factor)
    else:
        print('rubbish')