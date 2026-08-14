# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from tqdm import tqdm
from LucienUtil.SpeedUtil import SpeedUtil
os.environ['CUDA_VISIBLE_DEVICES'] = '2'

period = ['period1', 'period2', 'period3']
# PERIOD = ['period4']
fs_version = ['rffs']
# fs_version = ['fsv11']
# fs_version = ['rffs']
# fs_version = ['rffs', 'fsv8', 'fsv10', 'fsv11', 'fsrs']
label_flag = ['_pct']
model_select = ['XgbRegModel']
hyper_search_mode = ['False']
attend_ratio = ['45']

def wrapper(param_list):
    for param in tqdm(param_list):
        argv_list = ' '.join(list(param))
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v2_0_18/d20230810_factor_select_test/new_model_gain.py {argv_list}')
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v2_0_18/d20230810_factor_select_test/new_model_weight.py {argv_list}')
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v2_0_18/d20230810_factor_select_test/new_model_noEmotion.py {argv_list}')
#
param_list = list(product(period, fs_version, label_flag, model_select, hyper_search_mode, attend_ratio))
SpeedUtil.multiprocess(24, wrapper, param_list)

# SpeedUtil.multiprocess(1, wrapper, param_list)
# wrapper([param_list[0]])