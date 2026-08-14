# coding: utf-8
# Author：fengchi863
# Date ：2024/4/11 15:52

import shutil
import os
from tqdm import tqdm

d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
strategy_name = os.getcwd().split('/')[-3]
root_path = f'/data/user/015614/fcfactor/fefactorframework/batch_factor/{strategy_name}/{d_date}/{digging_name}/factor/'
copy_path = f'/data/user/015614/fcfactor/fefactorframework/NewNeptune/factor_20250522/'

submit_factors_name_list = [
'fc_n20250508_140',
'fc_n20250508_14',
'fc_n20250508_100',
'fc_n20250508_175',
'fc_n20250508_180',
'fc_n20250508_185',
'fc_n20250508_147',
'fc_n20250508_187',
'fc_n20250508_165',
'fc_n20250508_167',
'fc_n20250508_213',
'fc_n20250508_223',
'fc_n20250508_248',
'fc_n20250508_243',
'fc_n20250508_276',
'fc_n20250508_246',
'fc_n20250508_255',
'fc_n20250508_24',
'fc_n20250508_234',
'fc_n20250508_268',
'fc_n20250508_250',
'fc_n20250508_308',
'fc_n20250508_286',
'fc_n20250508_310',
'fc_n20250508_36',
'fc_n20250508_356',
'fc_n20250508_325',
'fc_n20250508_328',
'fc_n20250508_37',
'fc_n20250508_39',
'fc_n20250508_386',
'fc_n20250508_413',
'fc_n20250508_45',
'fc_n20250508_431',
'fc_n20250508_43',
                            ]

for idx, fname in enumerate(tqdm(submit_factors_name_list)):
    with open(root_path + f'factor_{fname}.py', 'r') as old_code:
        lines = old_code.readlines()

    fname_idx = idx+1
    with open(copy_path + f'factor_fc_n20250522_{fname_idx}.py', 'w') as new_code:
        for line in lines:
            if 'param1, param2' in line:
                parse1 = line.split('=')[1].split('#')[0]
                parse2 = parse1.replace('"', '').replace(' ', '').split(',')
                param1 = parse2[0]
                param2 = int(parse2[1])

            else:
                if 'param1' in line or 'param2' in line:
                    line = line.replace('param1', f'"{param1}"')
                    line = line.replace('param2', f'{param2}')
                # if '20250410' in line:
                #     line = line.replace('20250410', '20250522')
                if 'class' in line:
                    line = f'class factor_fc_n20250522_{fname_idx}(BaseFactor):\n'
                new_code.write(line)