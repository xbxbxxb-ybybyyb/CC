# coding: utf-8
# Author：fengchi863
# Date ：2022/12/14 23:44

"""
每年xquant的tradingday更新后跑出来
"""
from xquant.factordata import FactorData
import numpy as np

fd = FactorData()

date_list = fd.tradingday('20250101', '20251231', frequency='HALF')
date_list = fd.tradingday('20240101', '20241231', frequency='YEAR')
date_list = fd.tradingday('20230101', '20231231', frequency='DAY')
date_list = list(map(int, date_list))
date_list = np.array(date_list)
print(date_list)
pass