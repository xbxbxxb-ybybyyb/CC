# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from LucienUtil.SpeedUtil import SpeedUtil

# period = ['period1', 'period2', 'period3']
# period = ['period3', 'period3_roll']
period = ['period3']
# period = ['period2']
# period = ['period2_roll']
# period = ['period4']
# period = ['period5']
# period = ['period6']
fs_version = ['fsv8', 'fsv10', 'fsv11', 'fsrs', 'rffs']
# fs_version = ['fsrs']
label_flag = ['pct',]
model_select = ['XgbRegModel']
hyper_search_mode = ['False']
attend_ratio = ['40']
# seed = list(map(lambda x: str(x), list(range(0, 31))))
seed = ['0']

def wrapper(param_list):
    for param in param_list:
        argv_list = ' '.join(list(param))
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v4_0_7/model_all.py {argv_list}')

param_list = list(product(period, fs_version, label_flag, model_select, hyper_search_mode, attend_ratio, seed))
print(f'共训练{len(param_list)}个模型')
SpeedUtil.multiprocess(12, wrapper, param_list)
# wrapper([param_list[0]])
