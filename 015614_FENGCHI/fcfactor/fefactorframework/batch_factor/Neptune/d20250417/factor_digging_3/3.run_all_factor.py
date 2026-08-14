import sys
sys.path.append('/data/user/015614/fcfactor')
sys.path.append('/data/user/015614/fcfactor/fefactorframework')
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import datetime as dt
import os
import numpy as np

# factor_list = ['factor_fc_n20250314_1'] # 不能带.py
strategy = 'neptune'

cur_datetime = dt.datetime.today().strftime('%Y%m%d%H%M%S')
d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
strategy_name = os.getcwd().split('/')[-3]
dir_output = f'/data/user/015614/fefactorframework/{strategy}_{d_date}_{digging_name}/'
os.makedirs(dir_output, exist_ok=True)

factor_list = list()
for i in sorted(os.listdir(f'/data/user/015614/fcfactor/fefactorframework/batch_factor/{strategy_name}/{d_date}/{digging_name}/factor/')):
    if ".py" in i:
        factor_list.append(i.split(".py")[0])

# factor_list = factor_list[80:]
idx_list = np.append(np.arange(0, len(factor_list), 10), len(factor_list))  # 0-10已完成

for idx in range(1 , len(idx_list)):
    print(f'-----------{idx_list[idx-1]}:{min(len(factor_list)-1, idx_list[idx])}------------')
    batch_factor_list = factor_list[idx_list[idx-1]:min(len(factor_list), idx_list[idx])]
    res, check_res = Runner.run(factor_name_list=batch_factor_list, start_date=20160101, end_date=20191231, strategy=strategy,
                     output_dir=dir_output, # 结果的输出路径，包括回测报告等
                     options={
                         "calc.num_cpus": 10,
                         "local_evaluator": "",
                         'precheck': False,
                         "factor_test": True,
                         'report':False,
                         'mode': RunMode.research})
    for i in batch_factor_list:
        print(i)
        print('score:', check_res[i[7:] + '_' + strategy]['check_score_res'].loc['score', 'tot_score'])
        print('IC:', check_res[i[7:] + '_' + strategy]['corr_sta'].loc['corr_tot', 'value'])
        print('库内高相关因子：', check_res[i[7:] + '_' + strategy]['factor_corr_summary'])

