# @Time : 2021/3/5 10:03
# @Author : Zhichen Lu
# @File : online_tracing.py
from xquant.marketdata import MarketData
import pandas as pd
from online_conf import holding_info_path, daily_out_path, init_conf_path
import gc, os
import time, datetime
from dataApi.tradeDate import get_pre_trade_date
import configparser

date = int(datetime.date.today().strftime('%Y%m%d'))
conf = configparser.ConfigParser()
conf.read(init_conf_path + '%d.ini' % date)
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
    print(f'{now}:相对前日收益:{profit * 100 / pre_account_value}%, 收益额 {profit}')
    del online_data
    time.sleep(60)

{"command": "TARGET", "content": [{"portfolio": "201001", "symbol": "300550.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-12400.0"}},
                                  {"portfolio": "201001", "symbol": "300765.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-17400.0"}},
                                  {"portfolio": "201001", "symbol": "603995.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-15100.0"}},
                                  {"portfolio": "201001", "symbol": "002850.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-7900.0"}},
                                  {"portfolio": "201001", "symbol": "300454.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-3400.0"}},
                                  {"portfolio": "201001", "symbol": "300750.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-1900.0"}},
                                  {"portfolio": "201001", "symbol": "601689.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-30800.0"}},
                                  {"portfolio": "201001", "symbol": "002912.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-21800.0"}},
                                  {"portfolio": "201001", "symbol": "600681.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-32480.0"}},
                                  {"portfolio": "201001", "symbol": "300146.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "-35100.0"}},
                                  {"portfolio": "201001", "symbol": "603833.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "7400.0"}},
                                  {"portfolio": "201001", "symbol": "002791.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "4600.0"}},
                                  {"portfolio": "201001", "symbol": "300482.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "18000.0"}},
                                  {"portfolio": "201001", "symbol": "600958.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "102200.0"}},
                                  {"portfolio": "201001", "symbol": "605168.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "4700.0"}},
                                  {"portfolio": "201001", "symbol": "600392.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "48100.0"}},
                                  {"portfolio": "201001", "symbol": "601666.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "149300.0"}},
                                  {"portfolio": "201001", "symbol": "603587.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "40400.0"}},
                                  {"portfolio": "201001", "symbol": "300274.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "8200.0"}},
                                  {"portfolio": "201001", "symbol": "600847.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "27700.0"}},
                                  {"portfolio": "201001", "symbol": "600596.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "49600.0"}},
                                  {"portfolio": "201001", "symbol": "603356.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "24600.0"}},
                                  {"portfolio": "201001", "symbol": "601012.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "11500.0"}},
                                  {"portfolio": "201001", "symbol": "603223.SH", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "30100.0"}},
                                  {"portfolio": "201001", "symbol": "300587.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "79400.0"}},
                                  {"portfolio": "201001", "symbol": "000762.SZ", "target": {"StartTime": "10:00:00", "EndTime": "10:30:00", "TargetQty": "30600.0"}}],
 "shouldPause": 1}

{"command": "TARGET", "content": [{"portfolio": "201001", "symbol": "300550.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-12400.0"}},
                                  {"portfolio": "201001", "symbol": "300502.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-27900.0"}},
                                  {"portfolio": "201001", "symbol": "300765.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-9500.0"}},
                                  {"portfolio": "201001", "symbol": "603995.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-2250.0"}},
                                  {"portfolio": "201001", "symbol": "002850.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-7900.0"}},
                                  {"portfolio": "201001", "symbol": "300454.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-3400.0"}},
                                  {"portfolio": "201001", "symbol": "300750.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-1900.0"}},
                                  {"portfolio": "201001", "symbol": "002912.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-21800.0"}},
                                  {"portfolio": "201001", "symbol": "600681.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-6542.0"}},
                                  {"portfolio": "201001", "symbol": "300295.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-28800.0"}},
                                  {"portfolio": "201001", "symbol": "300146.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-35100.0"}},
                                  {"portfolio": "201001", "symbol": "300005.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-86600.0"}},
                                  {"portfolio": "201001", "symbol": "600348.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "-131200.0"}},
                                  {"portfolio": "201001", "symbol": "603897.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "39800.0"}},
                                  {"portfolio": "201001", "symbol": "300450.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "15800.0"}},
                                  {"portfolio": "201001", "symbol": "300472.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "87200.0"}},
                                  {"portfolio": "201001", "symbol": "300626.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "44100.0"}},
                                  {"portfolio": "201001", "symbol": "300548.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "28100.0"}},
                                  {"portfolio": "201001", "symbol": "002571.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "102900.0"}},
                                  {"portfolio": "201001", "symbol": "300707.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "26600.0"}},
                                  {"portfolio": "201001", "symbol": "300211.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "77200.0"}},
                                  {"portfolio": "201001", "symbol": "603186.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "25400.0"}},
                                  {"portfolio": "201001", "symbol": "603588.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "64400.0"}},
                                  {"portfolio": "201001", "symbol": "300517.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "38400.0"}},
                                  {"portfolio": "201001", "symbol": "300421.SZ", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "51300.0"}},
                                  {"portfolio": "201001", "symbol": "600007.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "31300.0"}},
                                  {"portfolio": "201001", "symbol": "601919.SH", "target": {"StartTime": "10:30:00", "EndTime": "11:00:00", "TargetQty": "48000.0"}}],
 "shouldPause": 1}

{"command": "TARGET", "content": [{"portfolio": "201001", "symbol": "300550.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-8100.0"}},
                                  {"portfolio": "201001", "symbol": "300502.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-27900.0"}},
                                  {"portfolio": "201001", "symbol": "002311.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-43.0"}},
                                  {"portfolio": "201001", "symbol": "300765.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-10700.0"}},
                                  {"portfolio": "201001", "symbol": "002850.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-7900.0"}},
                                  {"portfolio": "201001", "symbol": "300454.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-3400.0"}},
                                  {"portfolio": "201001", "symbol": "300750.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-1900.0"}},
                                  {"portfolio": "201001", "symbol": "000630.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-342200.0"}},
                                  {"portfolio": "201001", "symbol": "300721.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-67.0"}},
                                  {"portfolio": "201001", "symbol": "002912.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-21800.0"}},
                                  {"portfolio": "201001", "symbol": "600681.SH", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-42.0"}},
                                  {"portfolio": "201001", "symbol": "600549.SH", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-38080.0"}},
                                  {"portfolio": "201001", "symbol": "300295.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-28800.0"}},
                                  {"portfolio": "201001", "symbol": "300146.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-35100.0"}},
                                  {"portfolio": "201001", "symbol": "300005.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-86600.0"}},
                                  {"portfolio": "201001", "symbol": "600348.SH", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-35600.0"}},
                                  {"portfolio": "201001", "symbol": "603100.SH", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-21200.0"}},
                                  {"portfolio": "201001", "symbol": "002003.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-30.0"}},
                                  {"portfolio": "201001", "symbol": "300850.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-50.0"}},
                                  {"portfolio": "201001", "symbol": "002851.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "-66.0"}},
                                  {"portfolio": "201001", "symbol": "300756.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "31900.0"}},
                                  {"portfolio": "201001", "symbol": "603129.SH", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "8000.0"}},
                                  {"portfolio": "201001", "symbol": "603960.SH", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "32600.0"}},
                                  {"portfolio": "201001", "symbol": "600188.SH", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "60900.0"}},
                                  {"portfolio": "201001", "symbol": "300824.SZ", "target": {"StartTime": "11:00:00", "EndTime": "11:30:00", "TargetQty": "23600.0"}}],
 "shouldPause": 1}
