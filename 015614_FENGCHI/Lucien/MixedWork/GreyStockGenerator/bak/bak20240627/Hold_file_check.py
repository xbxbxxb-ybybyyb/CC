import sys
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import os

from xquant.factordata import FactorData

s = FactorData()

date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), 1)[0]
lastdate = s.tradingday(date, -2)[0]

path_hold = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/'
file_list = os.listdir(path_hold)
message = '！！！（新增成交记录）:'
for file in file_list:
    if lastdate in file or date in file:
        if 'jupiter成交记录-' not in file and \
                'saturn成交记录-' not in file and \
                'ceres成交记录-' not in file and \
                'Europa成交记录-' not in file and \
                'Metis成交记录-' not in file and \
                'Leda成交记录' not in file:
            message = message + file

if len(message) > 15:
    from xquant.xqutils.helper import link

    lm = link.LinkMessage()
    lm.sendMessage(message)
