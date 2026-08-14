import pandas as pd



import os
from xquant.factordata import FactorData
s = FactorData()

path1 = '/dfs/user/015585/00_hotspot/trade_all_time35/'
path2 = '/dfs/user/015585/00_hotspot/tick_all_time35/'


for path in [path1, path2]:
    file_list = os.listdir(path)
    file_list = [i.replace('.pkl','') for i in file_list]
    tradingday_list = s.tradingday(20150901,20231231)
    error_list = [i for i in tradingday_list if i not in file_list]
    print(path)
    print(len(error_list))
    print(error_list)





