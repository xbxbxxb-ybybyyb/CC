# coding: utf-8
# Author：fengchi863
# Date ：2024/8/28 19:37

import os
import subprocess
from itertools import product
from Zeus.ProjectSell.v2_0_0.config.strat_conf import *

config_list = ['config1']
period_list = ['period1', 'period2']
argv_list = tuple(product(config_list, period_list))

#%% 因为label只有label_list，所
# program_list = [f'python3 /data/user/015614/Lucien/Zeus/{STRATEGY_NAME}/{STRATEGY_VERSION}/label_generate/label_generate.py {config_list[x]}' for x in range(len(config_list))]
# processes = [subprocess.Popen(program, shell=True) for program in program_list]
# for process in processes:
#     process.wait()

program_list = [f'python3 /data/user/015614/Lucien/Zeus/{STRATEGY_NAME}/{STRATEGY_VERSION}/factor_select/factor_select_rffs.py {argv_list[x][0]} {argv_list[x][1]}' for x in range(len(argv_list))]

processes = [subprocess.Popen(program, shell=True) for program in program_list]    # 都在1分钟之内
for process in processes:
    process.wait()

