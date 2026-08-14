# @Time : 2021/1/24 11:31
# @Author : Zhichen Lu
# @File : download_data.py

import pandas as pd
from dataApi.getData import get_daily_1factor
from xquant.factordata import FactorData
import os



s = FactorData()

close = get_daily_1factor('close')
open_ = get_daily_1factor('open')

close.loc[20150201:20181231].to_excel('/data/user/015664/DownloadedData/close.xlsx')
open_.loc[20150201:20181231].to_excel('/data/user/015664/DownloadedData/open.xlsx')

total_market_value = s.get_factor_value('Basic_factor',[],s.tradingday('20150201','20180228'),['ev','a_mkt_cap'])
total_market_value = total_market_value.reset_index()
ev = total_market_value.pivot_table(index='mddate',columns='stock',values='ev')
a_mkt_cap = total_market_value.pivot_table(index='mddate',columns='stock',values='a_mkt_cap')


equitytototalcapital = s.get_factor_value('Basic_factor',[],s.tradingday('20150201','20180228'),['equitytototalcapital'])
equitytototalcapital = equitytototalcapital.reset_index()
equitytototalcapital = equitytototalcapital.pivot_table(index='mddate',columns='stock',values='equitytototalcapital')

ev.to_excel('/data/user/015664/DownloadedData/ev.xlsx')
a_mkt_cap.to_excel('/data/user/015664/DownloadedData/a_mkt_cap.xlsx')
equitytototalcapital.to_excel('/data/user/015664/DownloadedData/equitytototalcapital.xlsx')

