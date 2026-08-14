import pandas as pd
import xfactor.runner.BasicRunner as Runner
from settings import RunMode
import os
import shutil
from h5data.IO import IO
# factor_list = [
#     f'factor_qyh_neptune_shortterm_20250717_{i}' for i in range(1,11)
# # 'factor_qyh_neptunelong_shortterm_20250710_1',
# #     'factor_xbc_md_20250401_1'
#                ] # 不能带.py
factor_list = list(os.listdir('/data/user/015585/fefactorframework-mercury/factor/'))
factor_list = [x.replace('.py', '') for x in factor_list if 'emo' in x and '.py' in x]
factor_class_list = []
for x in factor_list:
    exec(f'from factor.{x} import {x}')
    exec(f'factor_class_list.append({x})')

strategy = 'europa'
output_dir = '/dfs/user/015585/01_factor_develop_store/fast_factor_newframe/europa/test_emo1/'

res, check_res = Runner.run(start_date=20170101, end_date=20250630, strategy=strategy,
                         output_dir=output_dir,
                         options={
                             "calc.num_cpus": 8,
                             "local_evaluator": "",
                             'precheck': False,
                             "factor_test": False,
                             'report':False,
                             'mode': RunMode.research},class_list_out=factor_class_list)



