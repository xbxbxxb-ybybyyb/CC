# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from LucienUtil.SpeedUtil import SpeedUtil
from Zeus.Neptune.v1_0_4.scripts.check_path_is_ok import check_path_is_ok
from tqdm import tqdm
import datetime as dt

"""
第五区间去掉除pct外的分场景
"""

# period = ['period4_fit', 'period5_fit', 'period6_fit']
# period = ['period7_fit']
# period = ['period1', 'period2']
# period = ['period1', 'period1_roll']
# period = ['period1']
# period = ['period1', 'period1_roll']
# period = ['period1', 'period2']
# period = ['period1', 'period2', 'period1_roll', 'period2_roll']
# period = ['period2']
# period = ['period2', 'period2_roll']
# period = ['period3']
# period = ['period3', 'period3_roll']
# period = ['period4']
period = ['period4', 'period4_roll']
# period = ['period5']
# period = ['period5', 'period5_roll']
# period = ['period6']
# period = ['period6', 'period6_roll']
# period = ['period7']
# period = ['period7', 'period7_roll']
# period = ['period8']
# period = ['period8', 'period8_roll']
# fs_version = ['fsv8', 'fsv10', 'fsv11', 'rffs']
# fs_version = ['fsv8', 'fsv10', 'fsv11']
fs_version = ['fsv8', 'fsv11']
# fs_version = ['fsv8', 'fsv10', 'rffs']
# fs_version = ['fsci']
# fs_version = ['fsv8']
# fs_version = ['rffs']
# fs_version = ['fsv10']
config_flag = [f'config{x}' for x in [1, 2, 3, 4, 5]]
# config_flag = [f'config{x}' for x in [6, 7, 8]]
# config_flag = [f'config{x}' for x in [  3, 4]]
# config_flag = [f'config{x}' for x in [2]]
# config_flag = [f'config{x}' for x in [1]]
# config_flag = [f'config{x}' for x in [4]]
label_trans = ['lt1']
# model_select = ['XgbRegModel', 'LgbRegModel']
model_select = ['XgbRegModel']
# model_select = ['LgbRegModel']
# hyper_search_mode = ['2']
hyper_search_mode = ['0']
# scaler_list = ['scaler1', 'scaler2']
scaler_list = ['scaler1']
attend_ratio = ['40']
seed = list(map(lambda x: str(x), list(range(0, 2))))
# seed = ['0']    # 0不在model_all里设置的范围内，所以应该是fix参数中的值

## 检测数据路径是否正确
# for config in config_flag:
#     check_path_is_ok(config)

def wrapper(param_list):
    for param in tqdm(param_list):
        argv_list = ' '.join(list(param))
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Neptune/v1_0_4/scripts/model_all.py {argv_list}')

param_list = list(product(period, fs_version, config_flag, label_trans, model_select, scaler_list, hyper_search_mode, attend_ratio, seed))

# param_list = list(filter(lambda x: x[2] + '_' + x[1] in ['config1_fsv10'], param_list))

# 当前有gpu_num个GPU
gpu_num = 3
for gpu_id in range(len(param_list)):
    param_list[gpu_id] = param_list[gpu_id] + (f'{gpu_id % gpu_num}',)

print(f'共训练{len(param_list)}个模型，当前时间为{dt.datetime.now()}')
SpeedUtil.multiprocess(3, wrapper, param_list)
# wrapper([param_list[0]])
# wrapper(param_list)
print(f'全部训练完毕，当前时间为{dt.datetime.now()}')