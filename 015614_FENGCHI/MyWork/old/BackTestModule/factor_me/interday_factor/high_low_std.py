# coding: utf-8
# Author：fengchi863
# Date ：2020/3/23 8:47

from config import *
import pandas as pd, numpy as np
from dataApi.interdayTest import FactorBackTest
start_date = 20170101
end_date = 20191231

high = get_daily_1factor('high')
low = get_daily_1factor('low')
temp_minutest_high_std = high.rolling(30).std()
temp_minutest_low_std = low.rolling(30).std()
factor = temp_minutest_high_std / temp_minutest_low_std

fbt = FactorBackTest(group=10)
fbt.load_factor(factor)
fbt.calc_group_ret()
print(fbt.calc_ic().mean()) # -0.000256
fbt.report(factor=factor, address=root_path, file_name='junk_factor')