import pandas as pd
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os
import shutil
from h5data.IO import IO
factor_list = [
    'factor_volume_time_smooth'
               ] # 不能带.py
strategy = 'neptune'
output_dir = '/data/user/023859/factor_test_research/'

if os.path.exists(f'{output_dir}precheck/{strategy}/same_test/'):
    list_file = os.listdir(f'{output_dir}precheck/{strategy}/same_test/')
    for i in list_file:
        for j in factor_list:
            if j.replace('factor_','') in i:
                os.remove(f'{output_dir}precheck/{strategy}/same_test/{i}')
                print('删除长短期检测文件，地址为:', f'{output_dir}precheck/{strategy}/same_test/{i}')

res, check_res = Runner.run(factor_name_list=factor_list, start_date=20170110, end_date=20201231, strategy=strategy,
                 output_dir=output_dir, # 结果的输出路径，包括回测报告等
                 options={
                     "calc.num_cpus": 1,
                     "local_evaluator": "",
                     'precheck': True,
                     "factor_test": True,
                     'report':True,
                     'mode': RunMode.research,})
for i in factor_list:
    print(i)
    print('score:', check_res[i[7:] + '_' + strategy]['check_score_res'].loc['score','tot_score'])
    print('IC:',check_res[i[7:] + '_' + strategy]['corr_sta'].loc['corr_tot', 'value'])
    print('库内高相关因子：', check_res[i[7:] + '_' + strategy]['factor_corr_summary'])


