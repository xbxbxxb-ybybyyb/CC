# coding: utf-8
# Author：fengchi863
# Date ：2024/3/19 17:10

import sys
sys.path.append('/data/user/015614/fcfactor')
sys.path.append('/data/user/015614/fcfactor/fefactorframework')
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import datetime as dt
import os

strategy = 'saturn'

cur_datetime = dt.datetime.today().strftime('%Y%m%d%H%M%S')
d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
dir_output = f'/data/user/015614/fefactorframework/{strategy}_{d_date}_{digging_name}/'
os.makedirs(dir_output, exist_ok=True)
os.chdir(f'/data/user/015614/fcfactor/fefactorframework/batch_factor/Saturn/{d_date}/{digging_name}/')

# factor_list = [f'factor_base']
factor_list = [f'factor_fc_n20250314_1']

# res, check_res = Runner.run(factor_name_list=factor_list, start_date=20191201, end_date=20201231, strategy=strategy,
res, check_res = Runner.run(factor_name_list=factor_list, start_date=20160101, end_date=20191231, strategy=strategy,
                 output_dir=dir_output, # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 1,
                     "local_evaluator": "",
                     'precheck': True,
                     "factor_test": True,
                     'report':True,
                     'mode': RunMode.research})
for i in factor_list:
    print(i)
    print(check_res[i[7:] + '_' + strategy].result_dic['check_score_res'].loc['score','tot_score'])
    print(check_res[i[7:] + '_' + strategy].result_dic['corr_sta'].loc['corr_tot', 'value'])
    print('库内高相关因子：', check_res[i[7:] + '_' + strategy].result_dic['factor_corr_summary'])
