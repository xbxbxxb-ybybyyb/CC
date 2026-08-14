# @Time : 2021/1/28 10:13
# @Author : Zhichen Lu
# @File : fakedata_generation.py

import pandas as pd
from dataApi.tradeDate import get_date_range
import shutil, os
from online_conf import local_config_path
import shutil

date_list = get_date_range(20210101, 20210114)

for date in date_list:
    shutil.copy('/data/group/800319/strategy_local_path/buy_time_info/20210127.pkl', '/data/group/800319/strategy_local_path3/buy_time_info/%d.pkl' % date)
