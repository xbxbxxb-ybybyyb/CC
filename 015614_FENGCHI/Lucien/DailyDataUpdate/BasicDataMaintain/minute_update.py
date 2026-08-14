import sys
import requests
import json

sys.path.append('/data/user/015614/Lucien')

from DailyDataUpdate.basicUpdate.minute_add import update_kline_by_stock, update_kline_by_stock_bench, \
    update_kline_by_factor, update_kline_by_factor_bench, get_bench_daily_data, \
    update_adjfactor_kline_by_factor, update_twap, update_twap_stock
from DailyDataUpdate.basicUpdate.daily import update_morning_data, update_limit_price
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

benchmarks = {'000300.SH': 'HS300', '000905.SH': 'ZZ500', '000906.SH': 'ZZ800','000001.SH': 'SZZZ', '399001.SZ': 'SZCZ',
              '000852.SH': 'ZZ1000', '000016.SH': 'SZ50', '399101.SZ': 'ZXBZ', '399102.SZ': 'CYBZ'}
minute_base_data_list = ['open', 'high', 'low', 'close', 'vol', 'amt', 'deal']

update_morning_data(address='/data/user/015614/easy_transfer/basic_data/daily')
update_kline_by_stock(line=48, store_address='/data/user/015614/easy_transfer/basic_data/minuteByStock')
send_message('minuteByStock updated')
update_kline_by_factor(line=20)
send_message('minuteByFactor updated')
update_adjfactor_kline_by_factor()
send_message('adjfactor_kline_by_factor updated')
update_kline_by_stock_bench(store_address='/data/user/015614/easy_transfer/basic_data/minuteByStockBench')
send_message('minuteByStockBench updated')

update_kline_by_factor_bench(line=1, factors=minute_base_data_list[:-1],
                       data_address='/data/user/015614/easy_transfer/basic_data/minuteByStockBench',
                       store_address='/data/user/015614/easy_transfer/basic_data/minuteByFactorBench',
                       desample_address='/data/user/015614/easy_transfer/basic_data/minuteDesampleByFactorBench')
send_message('minuteByFactorBench updated')
get_bench_daily_data()
send_message('bench_daily_data updated')
update_twap_stock()
update_twap(base_date=20100101, data_address='/data/user/015614/easy_transfer/basic_data/minuteByFactorBench',
            store_address='/data/user/015614/easy_transfer/basic_data/dailyBench')
send_message('twap updated')

update_limit_price()


