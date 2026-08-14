# @Time : 2021/3/5 10:03
# @Author : Zhichen Lu
# @File : online_tracing.py
from xquant.marketdata import MarketData
import pandas as pd
from online_conf import holding_info_path, daily_out_path,init_conf_path
import gc, os
import time, datetime
from dataApi.tradeDate import get_pre_trade_date
import  configparser


date = int(datetime.date.today().strftime('%Y%m%d'))
conf = configparser.ConfigParser()
conf.read(init_conf_path+'%d.ini'%date)
pre_account_value = eval(dict(conf['account_info'])['account_value'])

pre_date = get_pre_trade_date(date)
holding = pd.read_pickle(holding_info_path + '%d.pkl' % pre_date)
holding.pop('cash')
holding_stk = [x for x in holding]
#
md = MarketData()
#
while True:
    online_data = []
    for stk in holding_stk:
        temp_data = md.get_data_by_date('Stock', stk, date, ['3'])[-1:].set_index('HTSCSecurityID')
        online_data.append(temp_data[['LastPx', 'PreClosePx']])
    online_data = pd.concat(online_data)
    online_data['vol'] = pd.Series(holding)
    online_data['PreValue'] = online_data['vol'] * online_data['PreClosePx']
    online_data['pct_change'] = online_data['LastPx'] / online_data['PreClosePx'] - 1
    profit = (online_data['pct_change'] * online_data['PreValue']).sum()
    now = datetime.datetime.now().strftime('%H%M%S')
    print(f'{now}:相对前日收益:{profit*100 / pre_account_value}%, 收益额 {profit}')
    del online_data
    time.sleep(60)

    # date = 20210316
    # while True:
    # file_list = os.listdir(f'{daily_out_path}{date}/')
    # file_name = max(list(filter(lambda x: x.endswith('summary.pkl'), file_list)))
    # summary = pd.read_pickle(f'{daily_out_path}{date}/{file_name}')
#     cash = summary['bar_inital_cash']
#     holding = summary['barly_holding_info'].set_index('Symbol')
#     holding = holding[holding['NetPosition'] > 0]['NetPosition']
#     online_data = []
#     for stk in holding.index:
#         temp_data = md.get_data_by_date('Stock', stk, 20210315, ['3'])[-1:].set_index('HTSCSecurityID')
#         online_data.append(temp_data[['LastPx', 'PreClosePx']])
#     online_data = pd.concat(online_data)
#     online_data['vol'] = pd.Series(holding)
#     online_data['cap'] = online_data['vol'] * online_data['LastPx']
#     print(datetime.datetime.now(),(online_data['cap'].sum()+cash)/20046304.18 - 1)
#     time.sleep(60)

