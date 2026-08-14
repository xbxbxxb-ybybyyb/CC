

from LimitUpPredStrategy.backtest.strategy_backtest.StrategyTest import StrategyTest
import pandas as pd
from LimitUpPredStrategy.conf.path_conf import pred_output_path, bt_output_path
import requests
import json
def send_file(users, file):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    img_url = "http://168.7.124.15:1080/cgi-bin/media/upload?access_token={}&type=file".format(access_token)
    files = {'file': open(file, 'rb')}
    media_id = requests.post(img_url, files=files).json()['media_id']

    if isinstance(users, list):
        users = '|'.join(users)

    media = {"touser": users,
             "msgtype": "file",
             "agentid": 1000033,
             "file": {"media_id": media_id}}
    json_media = json.dumps(media, ensure_ascii=False).encode('utf-8')
    requests.post(post_url, json_media)
pred_file_name = '/rolling_catboost_reg_20210513/all_board_rolling_catboost_reg_20210513_trainPeriod60_predictPeriod5_factorNum80.pkl'
output_file_name = 'rolling_catboost_reg_20210513_all_board_rolling_catboost_reg_trainPeriod60_predictPeriod5_factorNum80'

factor = pd.read_pickle(pred_output_path + pred_file_name)['prediction']
signal = factor.copy()

self = StrategyTest(start_date=20150407, end_date=20201231, buy_money=3000000, buy_weight=0.1)
self.get_strategy_result(signal, N=30)  # 卖出周期为N分钟
result = self.statistic_factor(save_path=bt_output_path + output_file_name+'.xlsx')
#print(result)
send_file(['015630'],bt_output_path+output_file_name+'.xlsx')