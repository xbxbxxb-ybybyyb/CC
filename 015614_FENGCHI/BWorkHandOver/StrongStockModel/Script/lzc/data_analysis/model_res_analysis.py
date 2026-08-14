# @Time : 2021/3/13 15:50
# @Author : Zhichen Lu
# @File : model_res_analysis.py

import pandas as pd
import os
path = '/data/group/800319/signalForTest/'

file_list = os.listdir(path)
sign_file_list = list(filter(lambda x : x.startswith('sign_re'),file_list))
factor_file_list = list(filter(lambda x : x.startswith('factor_res'),file_list))

res = {}
for each in sign_file_list:
    res[each.replace('factor_result_signal_','facctor_').replace('_0.05.pkl','')] = pd.read_pickle(path+each)

for each in factor_file_list:
    res[each.replace('sign_result_signal_','signal_').replace('_0.05.pkl','')] = pd.read_pickle(path+each)

res = pd.DataFrame(res)
res.T.to_excel(path+'res.xlsx')