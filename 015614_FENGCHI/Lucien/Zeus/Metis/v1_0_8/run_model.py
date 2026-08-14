# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from LucienUtil.SpeedUtil import SpeedUtil

# period = ['period1', 'period2', 'period3']
# period = ['period4']
# period = ['period5']
period = ['period6']
fs_version = ['fsv8', 'fsv10', 'fsv11', 'fsrs', 'rffs']
label_flag = ['pct',]
model_select = ['XgbRegModel', 'LgbRegModel']
hyper_search_mode = ['True']
attend_ratio = ['40']

def wrapper(param_list):
    for param in param_list:
        argv_list = ' '.join(list(param))
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Metis/v1_0_8/model.py {argv_list}')

param_list = list(product(period, fs_version, label_flag, model_select, hyper_search_mode, attend_ratio))
print(f'共训练{len(param_list)}个模型')
SpeedUtil.multiprocess(12, wrapper, param_list)
# wrapper([param_list[0]])
