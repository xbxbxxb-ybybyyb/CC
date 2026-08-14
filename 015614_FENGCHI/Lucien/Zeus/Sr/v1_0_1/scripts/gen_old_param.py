# coding: utf-8
# Author：fengchi863
# Date ：2025/7/25 9:10

import shutil
import os

param_fpath = '/data/user/015614/Zeus/pred/Saturn/v6_0_3/config3/fsv8_s1_Xgb/period8/hyper/best_params.json'

os.makedirs('/data/user/015614/Zeus/pred/Sr/v1_0_1/config1/fsv8_s1_Xgb/period1/hyper/', exist_ok=True)
os.makedirs('/data/user/015614/Zeus/pred/Sr/v1_0_1/config2/fsv8_s1_Xgb/period1/hyper/', exist_ok=True)
os.makedirs('/data/user/015614/Zeus/pred/Sr/v1_0_1/config2/fsv10_s1_Xgb/period1/hyper/', exist_ok=True)
os.makedirs('/data/user/015614/Zeus/pred/Sr/v1_0_1/config3/fsv11_s1_Xgb/period1/hyper/', exist_ok=True)

shutil.copyfile(param_fpath, '/data/user/015614/Zeus/pred/Sr/v1_0_1/config1/fsv8_s1_Xgb/period1/hyper/best_params.json')
shutil.copyfile(param_fpath, '/data/user/015614/Zeus/pred/Sr/v1_0_1/config2/fsv8_s1_Xgb/period1/hyper/best_params.json')
shutil.copyfile(param_fpath, '/data/user/015614/Zeus/pred/Sr/v1_0_1/config2/fsv10_s1_Xgb/period1/hyper/best_params.json')
shutil.copyfile(param_fpath, '/data/user/015614/Zeus/pred/Sr/v1_0_1/config3/fsv11_s1_Xgb/period1/hyper/best_params.json')
