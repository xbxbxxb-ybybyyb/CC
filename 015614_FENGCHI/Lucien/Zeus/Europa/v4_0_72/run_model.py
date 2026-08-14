# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from LucienUtil.SpeedUtil import SpeedUtil
from tqdm import tqdm

# period = ['period1', 'period2', 'period3', 'period4']
# period = ['period1']
# period = ['period1', 'period1_roll']
period = ['period2']
# period = ['period2', 'period2_roll']
# period = ['period3']
# period = ['period3', 'period3_roll']
# period = ['period4']
# period = ['period4', 'period4_roll']
# period = ['period5']
# period = ['period5', 'period5_roll']
# period = ['period6']
# period = ['period6', 'period6_roll']
# period = ['period7']
# period = ['period7', 'period7_roll']
# period = ['period8']
# period = ['period8', 'period8_roll']
fs_version = ['fsv8', 'fsv10', 'fsv11', 'fsrs']
# fs_version = ['rffs']
# fs_version = ['fsv11', 'fsrs']
label_flag = ['p5',]
model_select = ['XgbRegModel', 'LgbRegModel']
# model_select = ['XgbRegModel']
# model_select = ['LgbRegModel']
# hyper_search_mode = ['1']
hyper_search_mode = ['0']
# scaler_list = ['scaler1', 'scaler2']
scaler_list = ['scaler1']
attend_ratio = ['40']
# seed = list(map(lambda x: str(x), list(range(0, 31))))
seed = ['0']    # 0不在model_all里设置的范围内，所以应该是fix参数中的值

def wrapper(param_list):
    for param in tqdm(param_list):
        argv_list = ' '.join(list(param))
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v4_0_72/model_all.py {argv_list}')

param_list = list(product(period, fs_version, label_flag, model_select, scaler_list, hyper_search_mode, attend_ratio, seed))
# param_list = list(filter(lambda x: x[1] + '_' + x[3] in ['fsv8_XgbRegModel', 'fsrs_XgbRegModel', 'rffs_XgbRegModel', 'fsv10_LgbRegModel', 'fsv8_LgbRegModel'], param_list))
print(f'共训练{len(param_list)}个模型')
SpeedUtil.multiprocess(24, wrapper, param_list)
# wrapper([param_list[0]])