# coding: utf-8
# Author：fengchi863
# Date ：2023/2/10 10:11

"""验证数据正确性"""

import pandas as pd

# 指数分钟数据 OK
# check = pd.read_hdf('/data/user/015614/easy_transfer/basic_data/minuteByStockBench/SZ50.h5')

# 股票分钟数据 OK 20150701开始，运行weekly_minute_update即可重刷
# check = pd.read_hdf('/data/user/015614/easy_transfer/basic_data/minuteByStock/600885.h5')

check = pd.read_hdf('/data/user/015614/easy_transfer/basic_data/daily/free_float_shares.h5')
print(1)