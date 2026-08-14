# coding: utf-8
# Author：fengchi863
# Date ：2020/3/20 10:36

from config import *
import pandas as pd, numpy as np
import time
import os
from multiprocessing import Pool
from dataApi.stockList import clean_stock_list
from dataApi.interdayTest import FactorBackTest

start_date = 20170101
end_date = 20191231
root_path = '/data/group/800319/junkData/temp_factor_by_fc/'

vol = get_daily_1factor('volume')
price = get_daily_1factor('close_badj')
factor = price.rolling(30).corr(vol).shift(1).loc[start_date:end_date]
# corr.to_hdf(root_path + 'alpha_test.h5', 'factor')

# 回测
fbt = FactorBackTest(group=10)
# factor = pd.read_hdf(root_path + 'alpha_test.h5', 'factor')
fbt.load_factor(factor)
fbt.calc_group_ret()
print(fbt.calc_ic().mean()) # -0.0053
fbt.report(factor=factor, address=root_path, file_name='junk_factor')